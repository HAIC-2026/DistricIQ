"""Core integration assertions against the actually migrated and seeded local database."""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.core.config import ROOT
from app.core.database import session
from app.main import app
from app.models.entities import ACSProfileObservation, District, Statistic
from pipelines.census.workbooks import FILES, parse_workbook

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def require_populated_database():
    if os.getenv("RUN_SEEDED_TESTS") != "1":
        pytest.skip("Set RUN_SEEDED_TESTS=1 for the local supplied-workbook validation")


def test_every_dashboard_value_and_moe_matches_its_original_workbook():
    with session() as db:
        actual = {s.id: s for s in db.scalars(select(Statistic).where(Statistic.source_id == "acs-2024-5yr"))}
        assert len(actual) == 3772
        for kind, name in FILES.items():
            expected = parse_workbook(ROOT / "data/raw/acs" / name, kind)
            for row in expected["statistics"]:
                stored = actual[row["id"]]
                for key in (
                    "estimate",
                    "moe",
                    "unit",
                    "reference_period",
                    "geography_id",
                    "variables",
                    "status",
                ):
                    assert getattr(stored, key) == row[key], (row["id"], key)
                assert stored.provenance["workbook_sha256"] == row["provenance"]["workbook_sha256"]
                assert stored.provenance["raw_estimate"] == row["provenance"]["raw_estimate"]
        assert db.scalar(select(func.count()).select_from(ACSProfileObservation)) == 44444
        assert db.scalar(select(func.count()).select_from(District)) == 76


def test_real_profiles_comparisons_geometry_and_sources():
    with TestClient(app) as client:
        assert client.get("/healthz").status_code == 200
        assert client.get("/readyz").status_code == 200
        for chamber, n, expected in [("house", 30, 51), ("senate", 15, 25)]:
            response = client.get(f"/v1/districts/{chamber}-{n:02}/profile")
            assert response.status_code == 200
            values = {s["indicator"]: s for s in response.json()["statistics"]}
            assert values["population"]["estimate"] > 0
            if chamber == "house":
                assert values["population"]["estimate"] == 34283
            comparison = client.get(f"/v1/districts/{chamber}-{n:02}/compare/county").json()
            assert comparison["benchmarks"]
            if chamber == "house":
                assert comparison["benchmarks"][0]["geography_id"] == "county-15003"
            state = client.get(f"/v1/districts/{chamber}-{n:02}/compare/state").json()
            assert state["benchmarks"][0]["geography_id"] == "state-15"
            assert (
                len(client.get(f"/v1/geography/districts?chamber={chamber}").json()["features"]) == expected
            )
            for metric in ("population", "median_household_income", "poverty_rate"):
                choropleth = client.get(
                    f"/v1/geography/choropleth?chamber={chamber}&indicator={metric}"
                ).json()
                assert len(choropleth["values"]) == expected
                assert choropleth["values"][f"{chamber}-{n:02}"] == values[metric]["estimate"]
        source = client.get("/v1/sources/acs-2024-5yr/workbooks/house")
        assert source.status_code == 200 and source.content[:2] == b"PK"
        with session() as db:
            lon, lat = db.execute(
                select(
                    func.ST_X(func.ST_PointOnSurface(District.geom)),
                    func.ST_Y(func.ST_PointOnSurface(District.geom)),
                ).where(District.id == "house-30")
            ).one()
        results = client.get(f"/v1/geography/point-lookup?lon={lon}&lat={lat}").json()
        assert any(d["id"] == "house-30" for d in results)


def test_every_legislative_district_profile_is_available():
    with TestClient(app) as client:
        districts = client.get("/v1/districts").json()
        assert len(districts) == 76
        for district in districts:
            response = client.get(f"/v1/districts/{district['id']}/profile")
            assert response.status_code == 200, district["id"]
            data = response.json()
            assert data["district"]["id"] == district["id"]
            assert len(data["statistics"]) == 46
            assert sum(s["estimate"] is not None for s in data["statistics"]) == 44
