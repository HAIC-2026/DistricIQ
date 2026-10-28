import json
import os

import pytest
from fastapi.testclient import TestClient

from app.ai.district_assistant import render
from app.ai.district_tools import Evidence
from app.main import app
from app.schemas.assistant import AnswerSelection
from app.services.program_service import get_program, search_programs
from pipelines.programs.ingest import ingest


@pytest.mark.integration
class TestPrograms:
    @pytest.fixture(autouse=True)
    def seeded(self):
        if os.getenv("RUN_SEEDED_TESTS") != "1":
            pytest.skip("Requires migrated directory")

    def test_idempotent_directory_retains_unverified_rules_and_dates(self):
        assert ingest()["programs"] == 16
        assert ingest()["programs"] == 16
        p = get_program("medquest")
        assert p["eligibility_status"] == "rules_incomplete"
        assert p["verification_date"] == "2026-10-26"
        assert "403" in p["rule_effective_date_or_version"]
        assert "CLOSED" in get_program("hcv")["application_availability"]

    def test_program_search_links_readonly_api_and_grounded_answer(self):
        results = search_programs("older retirement low income")
        assert any(p["id"] in {"ssi", "aabd", "msp", "extra-help"} for p in results)
        e = Evidence()
        e.dispatch("search_programs", json.dumps({"query": "older retirement low income"}))
        answer = render(
            AnswerSelection(
                intent="programs",
                fact_refs=[],
                comparison_refs=[],
                active_district_id=None,
                explanations=["eligibility"],
                program_ids=[p["id"] for p in e.programs[:3]],
            ),
            e,
        )
        assert answer["programs"] and answer["answerability"] == "program_information"
        assert "doesn't determine whether someone qualifies" in answer["message"]
        with TestClient(app) as client:
            assert len(client.get("/v1/programs").json()["programs"]) == 16
            for p in answer["programs"]:
                r = client.get(p["provenance_url"])
                assert r.status_code == 200 and r.json()["eligibility_url"] == p["eligibility_url"]
            assert client.post("/v1/programs/ssi", json={}).status_code == 405
            assert client.get("/v1/programs/invented").status_code == 404
