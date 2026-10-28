import json
import sys

import pytest

from app.core.config import ROOT
from app.discovery.geoportal_client import normalize

sys.path.insert(0, str(ROOT))


@pytest.fixture
def official_house():
    rows = json.loads((ROOT / "data/fixtures/dcat-snapshot.json").read_text())["data"]["dataset"]
    raw = next(r for r in rows if r["title"] == "Hawaii State House Districts 2022")
    d = normalize(raw)
    data = json.loads((ROOT / "data/fixtures/house.json").read_text())
    ids = json.loads((ROOT / "data/fixtures/house-ids.json").read_text())["features"]
    return d.model_copy(
        update={
            "validation_status": "service_inspected",
            "feature_count": 51,
            "available_fields": [f["name"] for f in data["fields"]],
            "inspection": {
                "name": data["name"],
                "fields": data["fields"],
                "identifier_field": "house_id",
                "feature_count": 51,
                "verified_identifiers": [f["attributes"]["house_id"] for f in ids],
                "geographic_vintage": 2022,
                "geometry_type": data["geometryType"],
                "queryable": True,
                "credits": data["copyrightText"],
                "description": data["description"],
            },
        }
    )
