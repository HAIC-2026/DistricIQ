import hashlib
import json
from datetime import UTC, datetime, timezone

from geoalchemy2.shape import from_shape

from app.core.config import ROOT
from app.core.database import session
from app.core.http import get_json
from app.discovery.arcgis_inspector import ArcGISInspector
from app.gis.geography import multipolygon, validate_features
from app.models.entities import District, Source


def fingerprint(inspection):
    keys = (
        "name",
        "fields",
        "identifier_field",
        "feature_count",
        "verified_identifiers",
        "geographic_vintage",
        "spatial_reference",
    )
    return hashlib.sha256(json.dumps({k: inspection[k] for k in keys}, sort_keys=True).encode()).hexdigest()


async def ingest(*, refresh=False):
    manifest = json.loads((ROOT / "data/manifests/sources.json").read_text())
    prepared = []
    for chamber, source in manifest["sources"].items():
        if source["status"] != "approved":
            raise ValueError(f"{chamber} requires local approve-source before ingestion")
        path = ROOT / "data/raw/geography" / f"{chamber}-2022.geojson"
        if path.is_file() and not refresh:
            payload = path.read_text()
            data = json.loads(payload)
            inspection = source["evaluation"]["dataset"]["inspection"]
            if inspection.get("geographic_vintage") != 2022 or fingerprint(inspection) != source.get(
                "metadata_fingerprint"
            ):
                raise ValueError("Stored official source inspection does not match approved plan metadata")
        else:
            inspection = await ArcGISInspector().inspect(source["url"], refresh=True)
            if fingerprint(inspection) != source.get("metadata_fingerprint"):
                raise ValueError("Source metadata changed since approval; review again")
            data = await get_json(
                source["url"] + "/query", {"f": "geojson", "where": "1=1", "outFields": "*", "outSR": 4326}
            )
            payload = json.dumps(data)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(payload)
        features = validate_features(data, chamber)
        prepared.append((chamber, source, inspection, features, hashlib.sha256(payload.encode()).hexdigest()))
    with session() as db, db.begin():
        for chamber, source, inspection, features, checksum in prepared:
            sid = f"{chamber}-boundaries-2022"
            db.merge(
                Source(
                    retrieved_at=datetime.now(timezone.utc),
                    id=sid,
                    title=inspection["name"],
                    url=source["url"],
                    status="approved",
                    metadata_record={
                        "inspection": inspection,
                        "approval": source,
                        "capture_sha256": checksum,
                        "local_file": f"data/raw/geography/{chamber}-2022.geojson",
                        "stored_crs": "EPSG:4326",
                        "official_identifier_field": chamber + "_id",
                    },
                )
            )
            db.flush()
            for feature in features:
                props = feature["properties"]
                number = int(props[chamber + "_id"])
                db.merge(
                    District(
                        id=f"{chamber}-{number:02}",
                        chamber=chamber,
                        number=number,
                        name=f"{chamber.title()} District {number}",
                        county=props.get("county"),
                        vintage=2022,
                        source_id=sid,
                        geom=from_shape(multipolygon(feature["geometry"]), srid=4326),
                    )
                )
    return {"house": 51, "senate": 25, "ingested_at": datetime.now(UTC).isoformat()}
