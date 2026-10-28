from fastapi.testclient import TestClient

from app.ai.discovery_agent import assist
from app.main import app, visits


def test_health_does_not_need_database_or_openai_key():
    with TestClient(app) as client:
        r = client.get("/healthz")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
        assert "api_key" not in str(r.json())


def test_versioned_api_contract_is_present():
    paths = app.openapi()["paths"]
    for path in (
        "/v1/discovery/search",
        "/v1/discovery/recommend",
        "/v1/discovery/evaluate",
        "/v1/discovery/datasets/{dataset_id}",
        "/v1/districts/{district_id}/profile",
        "/v1/geography/point-lookup",
        "/v1/statistics/{statistic_id}/provenance",
    ):
        assert path in paths


def test_invalid_inputs_rejected_without_network():
    with TestClient(app) as client:
        assert client.get("/v1/discovery/search?q=x").status_code == 422
        assert client.get("/v1/geography/point-lookup?lat=100&lon=0").status_code == 422
        assert client.post("/v1/discovery/recommend", json={"query": "test", "limit": 200}).status_code == 422
        assert (
            client.post("/v1/discovery/recommend", json={"query": "test", "unknown": True}).status_code == 422
        )
        assert client.post("/v1/discovery/approve", json={}).status_code == 404


async def test_missing_openai_key_deterministic_fallback(monkeypatch):
    import app.ai.discovery_agent as agent

    monkeypatch.setattr(agent, "client", lambda: None)
    result = await assist("house boundaries", {})
    assert result["status"] == "missing_key"
    assert not result["enabled"]


def test_discovery_rate_limit():
    visits.clear()
    with TestClient(app) as client:
        for _ in range(30):
            client.get("/v1/discovery/search?q=x")
        assert client.get("/v1/discovery/search?q=x").status_code == 429
    visits.clear()


def test_request_size_limit():
    with TestClient(app) as client:
        assert client.post("/v1/discovery/recommend", content="x" * 21000).status_code == 413


def test_recommendation_request_body_reaches_workflow(monkeypatch):
    from unittest.mock import AsyncMock

    from app.api.v1.discovery import workflow

    discover = AsyncMock(return_value={"query": "official house boundaries", "ai": {"enabled": False}})
    monkeypatch.setattr(workflow, "discover", discover)
    with TestClient(app) as client:
        response = client.post("/v1/discovery/recommend", json={"query": "official house boundaries"})
        assert response.status_code == 200
        assert response.json()["query"] == "official house boundaries"
    assert discover.call_args.args[0].query == "official house boundaries"
