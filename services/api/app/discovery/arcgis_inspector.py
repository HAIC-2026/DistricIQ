import re
import time
from datetime import datetime, timezone
from urllib.parse import urlsplit

from app.core.http import UpstreamUnavailable, get_json, safe_url
from app.schemas.discovery import Dataset


class InvalidLayer(ValueError):
    """A reachable service failed the required layer schema."""


class ArcGISInspector:
    def __init__(self):
        self.cache: dict[str, dict] = {}

    async def inspect(self, url: str, refresh: bool = False) -> dict:
        safe_url(url)
        if not re.search(r"/(MapServer|FeatureServer)/\d+$", urlsplit(url).path):
            raise ValueError("A numbered FeatureServer or MapServer layer is required")
        if url in self.cache and not refresh and time.time() - self.cache[url].get("cached_at", 0) < 3600:
            return self.cache[url]
        data = await get_json(url, {"f": "json"})
        if not isinstance(data, dict) or not data.get("fields") or not data.get("name"):
            raise InvalidLayer("Layer metadata is incomplete")
        fields = [f["name"] for f in data["fields"]]
        queryable = "query" in data.get("capabilities", "").lower()
        count = None
        ids = []
        identifier = next((f for f in ("house_id", "senate_id", "GEOID", "GEOID20") if f in fields), None)
        if queryable:
            count = (
                await get_json(url + "/query", {"f": "json", "where": "1=1", "returnCountOnly": "true"})
            ).get("count")
            # Verify actual attribute values, rather than treating catalog fields as evidence.
            if identifier and count is not None and count <= 100:
                response = await get_json(
                    url + "/query",
                    {"f": "json", "where": "1=1", "outFields": identifier, "returnGeometry": "false"},
                )
                ids = [f["attributes"].get(identifier) for f in response.get("features", [])]
        text = data.get("description", "")
        vintage_match = re.search(r"\b(20\d{2})\s+Hawaii State", text, re.I)
        result = {
            "available": True,
            "cached_at": time.time(),
            "name": data["name"],
            "layer_id": int(url.rsplit("/", 1)[1]),
            "geometry_type": data.get("geometryType"),
            "spatial_reference": data.get("extent", {}).get("spatialReference"),
            "extent": data.get("extent"),
            "fields": data["fields"],
            "identifier_field": identifier,
            "verified_identifiers": ids,
            "feature_count": count,
            "queryable": queryable,
            "maximum_record_count": data.get("maxRecordCount"),
            "output_formats": data.get("supportedQueryFormats"),
            "credits": data.get("copyrightText"),
            "geographic_vintage": int(vintage_match[1]) if vintage_match else None,
            "description": text,
            "restrictions": data.get("ownershipBasedAccessControlForFeatures"),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "raw": data,
        }
        self.cache[url] = result
        return result

    async def enrich(self, dataset: Dataset) -> Dataset:
        if not dataset.service_url:
            return dataset
        try:
            inspection = await self.inspect(dataset.service_url)
            return dataset.model_copy(
                update={
                    "inspection": inspection,
                    "geometry_type": inspection["geometry_type"],
                    "spatial_reference": inspection["spatial_reference"],
                    "available_fields": [f["name"] for f in inspection["fields"]],
                    "feature_count": inspection["feature_count"],
                    "validation_status": "service_inspected",
                }
            )
        except ValueError:
            return dataset.model_copy(update={"validation_status": "invalid_service"})
        except UpstreamUnavailable:
            return dataset.model_copy(update={"validation_status": "inspection_unavailable"})
