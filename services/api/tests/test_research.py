import json
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.ai import district_tools
from app.ai.district_assistant import render
from app.analytics.research_indicators import RAW
from app.core.database import session
from app.main import app
from app.models.entities import ACSProfileObservation
from app.schemas.assistant import AnswerSelection
from app.services import research_service as service


def test_semantic_discovery_matches_metadata_not_question_templates(monkeypatch):
    specs = service.catalog(native=False)
    monkeypatch.setattr(service, "catalog", lambda: specs)
    for query, code in [
        ("bachelor degree higher education", "dp02_r078_percent"),
        ("kupuna disability", "dp02_r090_estimate"),
        ("SNAP food benefits", "dp03_r082_estimate"),
        ("grandparents responsible grandchildren", "dp02_r052_estimate"),
        ("broadband internet subscription", "dp02_r174_estimate"),
        ("older adults living alone", "older_adults_living_alone"),
    ]:
        assert code in [r["code"] for r in service.search(query)], query
    assert service.search("quantum entanglement") == []


def test_context_requires_an_explicit_statistical_limitation():
    e = district_tools.Evidence()
    e.districts.add("house-30")
    e.facts["s1"] = {
        "ref": "s1",
        "statistic_id": "x",
        "estimate": 10,
        "moe": 2,
        "unit": "households",
        "geography": "House District 30",
        "label": "Households with Social Security income",
        "indicator": "dp03_r074_estimate",
        "reference_period": "2020–2024",
        "universe": "Households, all ages",
    }
    selection = AnswerSelection(
        intent="context", fact_refs=["s1"], comparison_refs=[], active_district_id="house-30", explanations=[]
    )
    with pytest.raises(ValueError, match="Context must"):
        render(selection, e)
    answer = render(selection.model_copy(update={"explanations": ["joint"]}), e)
    assert "exact count" in answer["message"]
    assert answer["answerability"] == "partially_answerable"
    assert "10 households" in answer["message"]
    assert "Separate figures do not tell us how many people" in answer["message"]


@pytest.mark.integration
class TestImportedProfiles:
    @pytest.fixture(autouse=True)
    def seeded(self):
        if os.getenv("RUN_SEEDED_TESTS") != "1":
            pytest.skip("Requires preserved populated PostgreSQL")

    def test_all_reviewed_measures_match_original_rows_and_citations(self):
        with session() as db:
            originals = {
                (r.profile, r.row_number): r
                for r in db.scalars(
                    select(ACSProfileObservation).where(ACSProfileObservation.geography_id == "house-30")
                )
            }
            for code, spec in RAW.items():
                value = service.observations("house-30", [code])[0]
                row = originals[(spec["profile"], spec["row"])]
                assert value["estimate"] == getattr(row, spec["measure"]), code
                assert value["moe"] == getattr(
                    row, "percent_moe" if spec["measure"] == "percent" else "moe"
                ), code
                assert value["provenance"]["estimate_cell"] == row.provenance["cells"][spec["measure"]]
                assert value["universe"]

    def test_actual_education_receipt_and_older_alone(self):
        codes = [
            "dp02_r078_percent",
            "dp03_r082_estimate",
            "dp03_r074_estimate",
            "older_adults_living_alone",
            "household_income_under_50000",
        ]
        values = {r["indicator"]: r for r in service.observations("house-30", codes)}
        assert (values[codes[0]]["estimate"], values[codes[0]]["moe"]) == (24.6, 2.2)
        assert (values[codes[1]]["estimate"], values[codes[1]]["moe"]) == (1660, 293)
        assert (values[codes[2]]["estimate"], values[codes[2]]["moe"]) == (2043, 215)
        assert values[codes[3]]["estimate"] == 367
        assert values[codes[3]]["moe"] == pytest.approx((57**2 + 95**2) ** 0.5)
        assert values[codes[4]]["estimate"] == 1971

    def test_computable_housing_burden_uses_all_three_denominators(self):
        rows = service.observations("house-30", ["housing_burden_30_plus", "housing_burden_30_plus_share"])
        assert rows[0]["estimate"] == 4146
        assert rows[1]["estimate"] == pytest.approx(4146 / (1751 + 719 + 5889) * 100)
        assert "computable" in rows[1]["universe"]
        assert len(rows[1]["provenance"]["inputs"]) == 4

    def test_invalid_indicators_geographies_and_readonly_routes(self):
        for geo, code in [
            ("house-99", "dp02_r078_percent"),
            ("county-99999", "dp02_r078_percent"),
            ("house-30", "DROP TABLE statistics"),
        ]:
            with pytest.raises((ValueError, KeyError)):
                service.observations(geo, [code])
        with TestClient(app) as client:
            found = client.get("/v1/research/indicators", params={"q": "education bachelor higher"})
            assert found.status_code == 200
            url = "/v1/research/observations/house-30/dp02_r078_percent/provenance"
            r = client.get(url)
            assert r.status_code == 200 and r.json()["provenance"]["estimate_cell"] == "DP78"
            assert client.post(url, json={}).status_code == 405

    def test_new_indicators_compare_districts_county_and_state(self):
        for args in [
            dict(right_id="house-31", benchmark=None),
            dict(right_id=None, benchmark="county"),
            dict(right_id=None, benchmark="state"),
        ]:
            e = district_tools.Evidence()
            r = e.dispatch(
                "compare_observations",
                json.dumps(dict(left_id="house-30", indicators=["dp02_r078_percent"], **args)),
            )
            assert len(r["comparisons"]) == 1
            assert r["comparisons"][0]["unit"] == "percentage points"
            assert all(f["universe"] == "Population 25 years and over" for f in r["facts"])

    def test_neighbor_comparisons_use_existing_polygons_and_same_chamber(self):
        ids = service.neighbors("house-30")
        assert ids and "house-30" not in ids and all(i.startswith("house-") for i in ids)
        e = district_tools.Evidence()
        r = e.dispatch(
            "compare_neighbors", json.dumps({"district_id": "house-30", "indicators": ["poverty_rate"]})
        )
        assert {f["geography_id"] for f in r["facts"]} == {"house-30", *ids}
        assert len(r["comparisons"]) == len(ids)
