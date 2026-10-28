"""Incremental, idempotent 2024 direct-SLD detailed tables. Never overwrites workbook data."""

import hashlib
import json
import re
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.analytics.acs import numeric
from app.core.config import ROOT, get_settings
from app.core.database import session
from app.core.http import get_json
from app.models.entities import District, Source, Statistic

BASE = "https://api.census.gov/data/2024/acs/acs5"
TABLES = {
    "B17001": "Poverty Status in the Past 12 Months by Sex by Age",
    "B25070": "Gross Rent as a Percentage of Household Income in the Past 12 Months",
    "B25007": "Tenure by Age of Householder",
    "B25011": "Tenure by Household Type (Including Living Alone) and Age of Householder",
    "B19037": "Age of Householder by Household Income in the Past 12 Months",
}
GEO = {
    "house": "state legislative district (lower chamber)",
    "senate": "state legislative district (upper chamber)",
    "county": "county",
    "state": "state",
}
EXPECTED = {
    "house": {f"{n:03}" for n in range(1, 52)},
    "senate": {f"{n:03}" for n in range(1, 26)},
    "county": {"001", "003", "005", "007", "009"},
    "state": {"15"},
}


def specs_from_metadata(table, metadata):
    if table not in TABLES:
        raise ValueError("Table is not approved for this acquisition")
    specs = {}
    variables = metadata.get("variables", {})
    for name, v in variables.items():
        if not re.fullmatch(table + r"_\d{3}E", name):
            continue
        base = name[:-1]
        if (
            base + "M" not in variables
            or not v.get("universe")
            or not v.get("concept", "").startswith(TABLES[table])
        ):
            raise ValueError("Unverified native table definition, universe or MOE")
        universe = v["universe"]
        unit = "people" if table == "B17001" else "households"
        specs[base] = {
            "code": base,
            "label": v["label"].removeprefix("Estimate!!").replace("!!", " / "),
            "unit": unit,
            "universe": universe,
            "denominator": None,
            "keywords": v["concept"],
            "native_estimate_variable": name,
            "native_moe_variable": base + "M",
            "source_id": "acs-2024-detailed-" + table,
            "reference_period": "2020–2024",
            "method": "reported",
            "table": table,
            "table_title": v["concept"],
        }
    if not specs or table + "_001" not in specs:
        raise ValueError("Table has no verified estimate variables")
    return dict(sorted(specs.items()))


def validate_rows(table, kind, data, specs):
    if not isinstance(data, list) or len(data) < 2:
        raise ValueError("Census returned no table data")
    header = data[0]
    if len(header) != len(set(header)) or any(
        k not in header for k in ["NAME", "GEO_ID", "state", GEO[kind]]
    ):
        raise ValueError("Unexpected Census geography/header schema")
    requested = [code + s for code in specs for s in ("E", "M")]
    if any(code not in header for code in requested):
        raise ValueError("Native estimate or MOE column missing")
    rows = []
    seen = set()
    for values in data[1:]:
        if len(values) != len(header):
            raise ValueError("Census row length mismatch")
        row = dict(zip(header, values))
        geocode = row[GEO[kind]]
        if row["state"] != "15" or geocode in seen:
            raise ValueError("Duplicate or non-Hawaiʻi geography")
        seen.add(geocode)
        rows.append(row)
    if seen != EXPECTED[kind]:
        raise ValueError(
            "Table geography identifiers do not match the 2022 Hawaiʻi plan/comparison geographies"
        )
    return rows


def persist_table(table, metadata, captures):
    specs = specs_from_metadata(table, metadata)
    manifest = json.loads((ROOT / "data/manifests/acs-compatibility.json").read_text())
    if (
        manifest.get("status"),
        manifest.get("state"),
        manifest.get("boundary_vintage"),
    ) != ("reviewed", "15", 2022):
        raise ValueError("Boundary compatibility approval missing")
    source_id = "acs-2024-detailed-" + table
    records = []
    for kind in GEO:
        capture = captures[kind]
        rows = validate_rows(table, kind, capture["data"], specs)
        for row in rows:
            code = row[GEO[kind]]
            gid = (
                f"{kind}-{int(code):02}"
                if kind in ("house", "senate")
                else "county-15" + code
                if kind == "county"
                else "state-15"
            )
            for variable, spec in specs.items():
                raw = {
                    variable + s: row.get(variable + s) for s in ("E", "M", "EA", "MA")
                }
                estimate, moe = (
                    numeric(raw[variable + "E"]),
                    numeric(raw[variable + "M"]),
                )
                if estimate is not None and estimate != int(estimate):
                    raise ValueError("Count table returned a non-integral estimate")
                records.append(
                    dict(
                        id=f"acs2024-native-{gid}-{variable}",
                        geography_id=gid,
                        geographic_level=kind,
                        boundary_vintage=2022 if kind in ("house", "senate") else None,
                        indicator=variable,
                        estimate=estimate,
                        moe=moe,
                        unit=spec["unit"],
                        reference_period="2020–2024",
                        variables=[variable + "E", variable + "M"],
                        method="direct",
                        status="available"
                        if estimate is not None
                        else "unavailable_or_suppressed",
                        source_id=source_id,
                        ingested_at=datetime.now(UTC),
                        provenance={
                            "variable_definition": spec["label"],
                            "universe": spec["universe"],
                            "table": table,
                            "table_title": spec["table_title"],
                            "variables": [variable + "E", variable + "M"],
                            "raw_values": raw,
                            "source_url": BASE,
                            "metadata_url": BASE + "/groups/" + table + ".json",
                            "request_parameters": capture["parameters"],
                            "geographic_identifier": {"state": "15", GEO[kind]: code},
                            "geographic_label": row["NAME"],
                            "census_geo_id": row["GEO_ID"],
                            "reference_period": "2020–2024",
                            "acs_geography_vintage": 2024,
                            "boundary_compatibility": manifest,
                            "moe_confidence": 0.9,
                            "raw_capture_sha256": capture["sha256"],
                            "retrieved_at": capture["retrieved_at"],
                        },
                    )
                )
    with session() as db, db.begin():
        district_ids = set(
            db.scalars(select(District.id).where(District.vintage == 2022))
        )
        if district_ids != {
            f"{k}-{int(n):02}" for k in ("house", "senate") for n in EXPECTED[k]
        }:
            raise ValueError(
                "Verified district polygons must exist before table ingestion"
            )
        db.merge(
            Source(
                id=source_id,
                title=f"2024 ACS five-year {table}: {next(iter(specs.values()))['table_title']}",
                url=BASE + "/groups/" + table + ".html",
                status="approved",
                metadata_record={
                    "table": table,
                    "release": 2024,
                    "reference_period": "2020–2024",
                    "boundary_compatibility": manifest,
                    "indicators": specs,
                    "geographies": 82,
                    "records": len(records),
                    "metadata_sha256": hashlib.sha256(
                        json.dumps(metadata, sort_keys=True).encode()
                    ).hexdigest(),
                    "acquired_at": datetime.now(UTC).isoformat(),
                },
            )
        )
        db.flush()
        for offset in range(0, len(records), 500):
            stmt = insert(Statistic).values(records[offset : offset + 500])
            db.execute(
                stmt.on_conflict_do_update(
                    index_elements=["id"],
                    set_={
                        c.name: stmt.excluded[c.name]
                        for c in Statistic.__table__.columns
                        if c.name != "id"
                    },
                )
            )
        count = db.scalar(
            select(func.count())
            .select_from(Statistic)
            .where(Statistic.source_id == source_id)
        )
        if count != len(records):
            raise ValueError(
                "Imported table count does not match complete native captures"
            )
    return {
        "table": table,
        "geographies": 82,
        "indicators": len(specs),
        "records": len(records),
        "source_id": source_id,
        "by_geography": {k: len(EXPECTED[k]) * len(specs) for k in GEO},
    }


async def ingest_table(table, *, refresh=False):
    if table not in TABLES:
        raise ValueError("Unsupported table")
    folder = ROOT / "data/raw/acs/2024/detailed" / table
    folder.mkdir(parents=True, exist_ok=True)
    metadata_path = folder / "metadata.json"
    if refresh or not metadata_path.exists():
        metadata = await get_json(BASE + "/groups/" + table + ".json")
        specs_from_metadata(table, metadata)
        metadata_path.write_text(json.dumps(metadata, indent=2))
    else:
        metadata = json.loads(metadata_path.read_text())
    specs = specs_from_metadata(table, metadata)
    captures = {}
    for kind, geography in GEO.items():
        path = folder / (kind + ".json")
        if refresh or not path.exists():
            key = get_settings().census_api_key.get_secret_value()
            if not key:
                raise ValueError(
                    "CENSUS_API_KEY must be configured and activated for new Census data queries"
                )
            params = {
                # The group already includes NAME; explicitly adding it duplicates the header.
                "get": "group(" + table + ")",
                "for": geography + ":*" if kind != "state" else "state:15",
            }
            if kind != "state":
                params["in"] = "state:15"
            data = await get_json(BASE, {**params, "key": key})
            validate_rows(table, kind, data, specs)
            capture = {
                "url": BASE,
                "parameters": params,
                "data": data,
                "retrieved_at": datetime.now(UTC).isoformat(),
                "sha256": hashlib.sha256(
                    json.dumps(data, sort_keys=True).encode()
                ).hexdigest(),
            }
            path.write_text(json.dumps(capture, indent=2))
        captures[kind] = json.loads(path.read_text())
        if (
            captures[kind]["sha256"]
            != hashlib.sha256(
                json.dumps(captures[kind]["data"], sort_keys=True).encode()
            ).hexdigest()
        ):
            raise ValueError("Native capture checksum mismatch")
    return persist_table(table, metadata, captures)
