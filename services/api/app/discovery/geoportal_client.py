import asyncio
import hashlib
import html
import json
import re
import time
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict

from app.core.config import ROOT, get_settings
from app.core.http import UpstreamUnavailable, get_json
from app.schemas.discovery import Dataset


class DCATCatalog(BaseModel):
    model_config = ConfigDict(extra="allow")
    dataset: list[dict]


class SearchPage(BaseModel):
    model_config = ConfigDict(extra="allow")
    features: list[dict]
    numberMatched: int
    numberReturned: int


def plain(value) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", str(value or ""))).strip()


def identity(record: dict) -> str:
    return hashlib.sha256(str(record).encode()).hexdigest()[:24]


def canonical_id(service: str | None, identifier: str) -> str:
    return hashlib.sha256((service or identifier).rstrip("/").encode()).hexdigest()[:24]


def metadata_date(value) -> str | None:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, timezone.utc).isoformat()
    return str(value) if value else None


def normalize(raw: dict, retrieved_at: str | None = None) -> Dataset:
    is_search = "properties" in raw
    r = raw.get("properties", raw)
    distributions = r.get("distribution", [])
    service = (
        r.get("url")
        if is_search
        else next(
            (x.get("accessURL") for x in distributions if "GeoServices REST" in x.get("format", "")), None
        )
    )
    # Only a numbered ArcGIS layer can be inspected as a candidate layer.
    service = service if service and re.search(r"/(MapServer|FeatureServer)/\d+$", service) else None
    title = plain(r.get("title", "Untitled"))
    description = plain(r.get("description"))
    level = (
        "house"
        if re.search(r"state house", title, re.I)
        else "senate"
        if re.search(r"state senate", title, re.I)
        else "tract"
        if re.search(r"census tract", title, re.I)
        else None
    )
    years = re.findall(r"\b(?:19|20)\d{2}\b", title)
    vintage = int(years[-1]) if years and level else None
    publisher = r.get("publisher", {}).get("name") if not is_search else r.get("source")
    identifier = str(r.get("identifier") or raw.get("id") or r.get("id") or identity(raw))
    catalog = r.get("landingPage") or (
        f"https://geoportal.hawaii.gov/api/search/v1/collections/dataset/items/{raw.get('id')}"
        if is_search
        else None
    )
    spatial = (
        r.get("spatial") or json.dumps(r.get("extent")) if (r.get("spatial") or r.get("extent")) else None
    )
    values = dict(
        dataset_id=canonical_id(service, identifier),
        title=title,
        description=description,
        publisher=publisher,
        provider="Hawaiʻi Geoportal",
        catalog_url=catalog,
        official_source_url=service or catalog,
        service_url=service,
        download_url=next((x.get("accessURL") for x in distributions if x.get("format") == "GeoJSON"), None),
        format="ArcGIS REST" if service else None,
        geographic_coverage=spatial,
        geographic_level=level,
        geographic_vintage=vintage,
        publication_date=metadata_date(r.get("created") if is_search else r.get("issued")),
        modified_date=metadata_date(r.get("modified")),
        license=plain(r.get("licenseInfo") if is_search else r.get("license")) or None,
        keywords=r.get("tags", []) if is_search else r.get("keyword", []),
        access_level=r.get("access") if is_search else r.get("accessLevel"),
        raw_metadata=raw,
    )
    if retrieved_at:
        values["retrieved_at"] = retrieved_at
    return Dataset(**values)


class GeoportalClient:
    def __init__(self):
        self.settings = get_settings()
        self.records: dict[str, Dataset] = {}
        self.mode = "unavailable"
        self.warning: str | None = None
        self._catalog: list[Dataset] | None = None
        self._catalog_loaded = 0.0
        self._lock = asyncio.Lock()

    def _remember(self, records):
        for r in records:
            self.records[r.dataset_id] = r
        return list({r.dataset_id: r for r in records}.values())

    async def list_catalog_datasets(self) -> list[Dataset]:
        async with self._lock:
            if (
                self._catalog is not None
                and time.time() - self._catalog_loaded < self.settings.cache_ttl_seconds
            ):
                return self._catalog
            path = self.settings.cache_dir / "dcat.json"
            cached = None
            try:
                cached = json.loads(path.read_text())
            except (OSError, ValueError):
                pass
            if cached and time.time() - cached.get("saved_at", 0) < self.settings.cache_ttl_seconds:
                envelope = cached
                self.mode = "cached_dcat"
            else:
                try:
                    data = DCATCatalog.model_validate(
                        await get_json(self.settings.geoportal_dcat_url)
                    ).model_dump()
                    envelope = {
                        "saved_at": time.time(),
                        "retrieved_at": datetime.now(timezone.utc).isoformat(),
                        "source_url": self.settings.geoportal_dcat_url,
                        "data": data,
                    }
                    path.parent.mkdir(parents=True, exist_ok=True)
                    temp = path.with_suffix(".tmp")
                    temp.write_text(json.dumps(envelope))
                    temp.replace(path)
                    self.mode = "live_dcat"
                except (UpstreamUnavailable, ValueError):
                    # A checked-in, real capture is explicitly labelled stale; never a fabricated fallback.
                    if cached:
                        envelope = cached
                    else:
                        try:
                            envelope = json.loads((ROOT / "data/fixtures/dcat-snapshot.json").read_text())
                        except (OSError, ValueError) as exc:
                            raise UpstreamUnavailable(
                                "Geoportal unavailable and no catalog snapshot exists"
                            ) from exc
                    self.mode = "stale_dcat"
                    self.warning = "Live catalog unavailable. Showing a previously retrieved snapshot; reverify before ingestion."
            parsed = DCATCatalog.model_validate(envelope["data"])
            self._catalog = self._remember([normalize(r, envelope["retrieved_at"]) for r in parsed.dataset])
            self._catalog_loaded = time.time()
            return self._catalog

    async def search_datasets(self, query: str, limit: int = 20) -> list[Dataset]:
        if not 1 <= limit <= 100 or not 1 <= len(query) <= 500:
            raise ValueError("Invalid search bounds")
        rows: list[Dataset] = []
        try:
            # Verified OpenAPI: q, limit<=100, one-based startindex, FeatureCollection response.
            start = 1
            for _ in range(10):
                page = SearchPage.model_validate(
                    await get_json(
                        self.settings.geoportal_search_api + "/collections/dataset/items",
                        {"q": query, "limit": min(20, limit), "startindex": start},
                    )
                )
                rows.extend(normalize(r) for r in page.features)
                if len(self._remember(rows)) >= limit or page.numberReturned == 0:
                    break
                start += page.numberReturned
                if start > page.numberMatched:
                    break
            self.mode = "live_search"
            self.warning = None
            return self._remember(rows)[:limit]
        except (UpstreamUnavailable, ValueError):
            records = await self.list_catalog_datasets()
            self.warning = self.warning or "Search API unavailable. Using the DCAT catalog."
            terms = set(re.findall(r"[a-z]{3,}", query.lower())) - {
                "find",
                "best",
                "official",
                "hawaii",
                "state",
                "the",
                "for",
                "latest",
                "data",
                "dataset",
            }

            def matches(r):
                text = (r.title + " " + " ".join(r.keywords)).lower()
                return sum(term in text for term in terms)

            return sorted((r for r in records if matches(r)), key=lambda r: (-matches(r), r.dataset_id))[
                :limit
            ]

    async def get_dataset_metadata(self, dataset_id: str) -> Dataset:
        if dataset_id not in self.records:
            await self.list_catalog_datasets()
        if dataset_id not in self.records:
            raise KeyError(dataset_id)
        return self.records[dataset_id]

    async def get_dataset_distributions(self, dataset_id: str):
        r = await self.get_dataset_metadata(dataset_id)
        return r.raw_metadata.get("distribution", [])
