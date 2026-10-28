"""Verified DBEDT table 1.06 adapter. Keep annual estimates separate from ACS survey estimates."""

import hashlib
import io
import json
from datetime import datetime, timezone

import httpx
import pandas as pd

from app.core.config import ROOT
from app.core.database import session
from app.core.http import UpstreamUnavailable, safe_url
from app.models.entities import Source, Statistic

URL = "https://files.hawaii.gov/dbedt/economic/archive/databook/db2024/section01.xls"
TITLE = "Table 1.06-- RESIDENT POPULATION, BY COUNTY:  2010 TO 2024"


def parse_population(content: bytes):
    if not content.startswith(bytes.fromhex("D0CF11E0")):
        raise ValueError("Expected an official XLS workbook, not an HTML response")
    frame = pd.read_excel(io.BytesIO(content), sheet_name="01.06", header=None, engine="xlrd")
    if (
        frame.iat[0, 0] != TITLE
        or frame.iat[6, 2] != "State total"
        or "Including Kalawao" not in str(frame.iat[33, 0])
    ):
        raise ValueError("DBEDT schema or footnote changed; manual review required")
    selected = frame.loc[frame[0].astype(str).eq("2024:")]
    if len(selected) != 1 or selected.iloc[0, 1] != "July 1":
        raise ValueError("Expected one July 1, 2024 record")
    row = selected.iloc[0]
    geographies = [
        ("state-15", 2, "state"),
        ("county-15003", 3, "county"),
        ("county-15001", 4, "county"),
        ("county-15007", 5, "county"),
        ("county-group-maui-kalawao", 6, "county_group"),
    ]
    records = []
    for gid, col, level in geographies:
        value = float(row[col])
        if not value.is_integer() or value <= 0:
            raise ValueError("Invalid official population estimate")
        records.append(
            {
                "geography_id": gid,
                "geographic_level": level,
                "estimate": value,
                "cell": f"{chr(65 + col)}{int(selected.index[0]) + 1}",
            }
        )
    if records[0]["estimate"] != sum(r["estimate"] for r in records[1:]):
        raise ValueError("County totals do not conserve statewide population")
    return records


async def capture():
    safe_url(URL)
    async with httpx.AsyncClient(timeout=30, follow_redirects=False, trust_env=False) as client:
        async with client.stream("GET", URL) as response:
            response.raise_for_status()
            content = bytearray()
            async for chunk in response.aiter_bytes():
                content.extend(chunk)
                if len(content) > 8_000_000:
                    raise UpstreamUnavailable("Workbook size limit exceeded")
    content = bytes(content)
    records = parse_population(content)
    path = ROOT / "data/raw/dbedt"
    path.mkdir(parents=True, exist_ok=True)
    (path / "section01-2024.xls").write_bytes(content)
    return content, records


async def ingest():
    manifest = json.loads((ROOT / "data/manifests/dbedt.json").read_text())
    if manifest["status"] != "approved":
        raise ValueError("Review table evidence and run approve-dbedt first")
    content, records = await capture()
    if hashlib.sha256(content).hexdigest() != manifest["sha256"]:
        raise ValueError("DBEDT workbook changed since approval")
    with session() as db, db.begin():
        db.merge(
            Source(
                retrieved_at=datetime.now(timezone.utc),
                id="dbedt-2024-table-106",
                title="DBEDT 2024 Data Book, table 1.06",
                url=URL,
                status="approved",
                metadata_record=manifest,
            )
        )
        db.flush()
        for record in records:
            db.merge(
                Statistic(
                    ingested_at=datetime.now(timezone.utc),
                    id="dbedt2024-" + record["geography_id"],
                    geography_id=record["geography_id"],
                    geographic_level=record["geographic_level"],
                    boundary_vintage=None,
                    indicator="dbedt_resident_population",
                    estimate=record["estimate"],
                    moe=None,
                    unit="people",
                    reference_period="2024-07-01",
                    variables=["01.06!" + record["cell"]],
                    method="direct",
                    status="available",
                    source_id="dbedt-2024-table-106",
                    provenance={
                        "source_url": URL,
                        "table": "1.06",
                        "cell": record["cell"],
                        "sha256": manifest["sha256"],
                        "footnote": "Maui includes Kalawao County. Annual population estimate; not an ACS estimate; not district-level.",
                        "moe_status": "not published in table",
                    },
                )
            )
    return {"records": len(records), "reference_date": "2024-07-01"}
