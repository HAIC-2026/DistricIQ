import json
from datetime import UTC, datetime, timezone

from sqlalchemy import select

from app.analytics.acs import INDICATORS, calculate
from app.core.config import ROOT, get_settings
from app.core.database import session
from app.core.http import get_json
from app.models.entities import District, Source, Statistic

BASE = "https://api.census.gov/data/2024/acs/acs5"
COMPATIBILITY = "https://www.census.gov/programs-surveys/acs/technical-documentation/table-and-geography-changes/2024/geography-changes.html"
GEOGRAPHIES = {
    "house": "state legislative district (lower chamber)",
    "senate": "state legislative district (upper chamber)",
    "county": "county",
    "state": "state",
}


async def fetch_geography(kind: str):
    geo = GEOGRAPHIES[kind]
    variables = sorted({v + s for spec in INDICATORS.values() for v in spec["variables"] for s in ("E", "M")})
    merged: dict[str, dict] = {}
    for offset in range(0, len(variables), 46):
        requested = variables[offset : offset + 46]
        params = {"get": "NAME," + ",".join(requested), "for": f"{geo}:*" if kind != "state" else "state:15"}
        if kind != "state":
            params["in"] = "state:15"
        if get_settings().census_api_key.get_secret_value():
            params["key"] = get_settings().census_api_key.get_secret_value()
        data = await get_json(BASE, params)
        if not isinstance(data, list) or len(data) < 2 or "NAME" not in data[0] or geo not in data[0]:
            raise ValueError("Unexpected Census response schema")
        if any(v not in data[0] for v in requested):
            raise ValueError("Census response is missing requested variables")
        capture = {
            "url": BASE,
            "parameters": {k: v for k, v in params.items() if k != "key"},
            "data": data,
            "retrieved_at": datetime.now(UTC).isoformat(),
        }
        raw = ROOT / "data/raw/census"
        raw.mkdir(parents=True, exist_ok=True)
        (raw / f"2024-{kind}-{offset}.json").write_text(json.dumps(capture))
        current = {}
        for values in data[1:]:
            if len(values) != len(data[0]):
                raise ValueError("Census row length mismatch")
            row = dict(zip(data[0], values))
            if row.get("state") != "15":
                raise ValueError("Non-Hawaiʻi ACS record")
            code = row[geo]
            if code in current:
                raise ValueError("Duplicate Census geography")
            current[code] = row
        if merged and set(current) != set(merged):
            raise ValueError("Census batch geography mismatch")
        for code, row in current.items():
            merged.setdefault(code, {}).update(row)
    expected = {"house": 51, "senate": 25, "county": 5, "state": 1}[kind]
    if len(merged) != expected:
        raise ValueError("Incomplete ACS geography coverage")
    if kind in ("house", "senate") and sorted(int(x) for x in merged) != list(range(1, expected + 1)):
        raise ValueError("ACS district identifiers do not match")
    return merged


async def ingest(*, live=False):
    if not live:
        from pipelines.census.workbooks import ingest_local

        return ingest_local()

    # Check explicit Hawaiʻi 2024/2022 compatibility review before mapping by district identifier.
    manifest = json.loads((ROOT / "data/manifests/acs-compatibility.json").read_text())
    if (
        manifest.get("status") != "reviewed"
        or manifest.get("state") != "15"
        or manifest.get("boundary_vintage") != 2022
    ):
        raise ValueError("Boundary compatibility review is required")
    datasets = {}
    for kind in GEOGRAPHIES:
        datasets[kind] = await fetch_geography(kind)
    with session() as db, db.begin():
        districts = list(db.scalars(select(District)))
        if len(districts) != 76 or any(d.vintage != 2022 for d in districts):
            raise ValueError("Ingest all verified 2022 district geometry first")
        source = Source(
            retrieved_at=datetime.now(timezone.utc),
            id="acs-2024-5yr",
            title="2024 ACS five-year detailed tables (2020–2024)",
            url=BASE,
            status="approved",
            metadata_record={"reference_period": "2020–2024", "boundary_compatibility": manifest},
        )
        db.merge(source)
        db.flush()
        count = 0
        for kind, rows in datasets.items():
            for geocode, row in rows.items():
                gid = (
                    f"{kind}-{int(geocode):02}"
                    if kind in ("house", "senate")
                    else "county-15" + geocode
                    if kind == "county"
                    else "state-15"
                )
                for code in INDICATORS:
                    values = calculate(row, code)
                    raw_values = values.pop("raw_values")
                    db.merge(
                        Statistic(
                            ingested_at=datetime.now(timezone.utc),
                            id=f"acs2024-{gid}-{code}",
                            geography_id=gid,
                            geographic_level=GEOGRAPHIES[kind],
                            boundary_vintage=2022 if kind in ("house", "senate") else None,
                            indicator=code,
                            reference_period="2020–2024",
                            source_id=source.id,
                            **values,
                            provenance={
                                "source_url": BASE,
                                "geography": {"state": "15", GEOGRAPHIES[kind]: geocode},
                                "variables": values["variables"],
                                "raw_values": raw_values,
                                "boundary_compatibility_url": COMPATIBILITY,
                                "moe_confidence": 0.90,
                                "moe_method": "Published MOE; derived sums use RSS and subset rates use ACS approximation; covariance unavailable.",
                            },
                        )
                    )
                    count += 1
        return {"geographies": sum(map(len, datasets.values())), "statistics": count}
