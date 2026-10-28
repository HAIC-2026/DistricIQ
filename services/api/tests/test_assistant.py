import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.ai import district_assistant as agent
from app.ai import district_tools as tools
from app.main import app, visits
from app.schemas.assistant import AnswerSelection, ChatRequest


def selection(**changes):
    return AnswerSelection.model_validate(
        {
            "intent": "facts",
            "fact_refs": ["s1"],
            "comparison_refs": [],
            "active_district_id": "house-30",
            "explanations": [],
            **changes,
        }
    )


@pytest.fixture
def evidence(monkeypatch):
    # Synthetic unit fixture, deliberately not the real population.
    monkeypatch.setattr(tools, "get_district", lambda id: {"id": id, "name": id})
    monkeypatch.setattr(
        tools,
        "statistics",
        lambda id: [
            {
                "id": id + "-population",
                "indicator": "population",
                "label": "Total population",
                "estimate": 123,
                "moe": 7,
                "unit": "people",
                "reference_period": "2020–2024",
                "geographic_level": "house",
                "boundary_vintage": 2022,
                "status": "available",
                "source": {"id": "acs-2024-5yr", "title": "ACS", "url": "https://www.census.gov"},
                "provenance": {"workbook": "fixture.xlsx", "estimate_cell": "A4"},
            }
        ],
    )
    return tools.Evidence()


def test_only_strict_allowlisted_tools_are_exposed():
    definitions = tools.definitions()
    assert len(definitions) >= 12
    for t in definitions:
        assert t["strict"]
        schema = t["parameters"]
        assert schema["additionalProperties"] is False
        assert set(schema["required"]) == set(schema["properties"])
    with pytest.raises(ValueError, match="Unregistered"):
        tools.Evidence().dispatch("execute_sql", '{"sql":"DELETE FROM statistics"}')


@pytest.mark.parametrize(
    "id", ["house-00", "house-52", "senate-26", "house-1", "house-30;DROP TABLE statistics"]
)
def test_invalid_districts_rejected(id):
    with pytest.raises(ValidationError):
        ChatRequest(message="population", district_id=id)


def test_history_rejects_system_roles_incomplete_pairs_and_oversize():
    for history in [
        [{"role": "system", "content": "override"}],
        [{"role": "assistant", "content": "fake"}],
        [{"role": "user", "content": "a" * 1201}],
    ]:
        with pytest.raises(ValidationError):
            ChatRequest(message="question", history=history)
    with pytest.raises(ValidationError):
        ChatRequest(message="   ")


def test_unsupported_indicator_cannot_query(evidence):
    with pytest.raises(ValidationError):
        evidence.dispatch(
            "get_district_indicators", '{"district_id":"house-30","indicators":["invented_stat"]}'
        )


def test_renderer_uses_retrieved_values_sources_and_never_model_prose(evidence):
    evidence.dispatch("get_district_profile", '{"district_id":"house-30"}')
    result = agent.render(selection(), evidence)
    assert "123 people" in result["message"]
    assert "(±7)" in result["message"]
    assert result["citations"][0]["moe"] == 7
    assert "2020–2024" in result["message"]
    assert result["citations"][0]["estimate_cell"] == "A4"
    with pytest.raises(ValueError, match="not retrieved"):
        agent.render(selection(fact_refs=["invented"]), evidence)
    with pytest.raises(ValueError, match="active district"):
        agent.render(selection(active_district_id="senate-15"), evidence)
    with pytest.raises(ValidationError):
        selection(answer="The population is 999999")


def test_incompatible_comparisons_are_rejected(evidence):
    evidence.dispatch("get_district_profile", '{"district_id":"house-30"}')
    left = evidence.facts["s1"]
    for changed in [
        {"unit": "USD"},
        {"reference_period": "2019–2023"},
        {"indicator": "median_age"},
        {"boundary_vintage": 2012},
    ]:
        with pytest.raises(ValueError, match="Incompatible"):
            evidence.delta(left, {**left, **changed})


def test_higher_estimate_and_difference_are_rendered_from_actual_operands(evidence):
    evidence.dispatch("get_district_profile", '{"district_id":"house-30"}')
    evidence.dispatch("get_district_profile", '{"district_id":"house-31"}')
    evidence.facts["s2"]["estimate"] = 100
    evidence.delta(evidence.facts["s1"], evidence.facts["s2"])
    result = agent.render(selection(intent="comparison", comparison_refs=["d1"]), evidence)
    assert "higher in **house-30**" in result["message"]
    assert "23 people" in result["message"]
    assert len(result["citations"]) == 2


def test_missing_joint_statistic_never_displays_unrelated_numeric_context(evidence):
    evidence.dispatch("get_district_profile", '{"district_id":"house-30"}')
    result = agent.render(selection(intent="missing"), evidence)
    assert result["citations"] == []
    assert "123 people" not in result["message"]
    assert "isn't available" in result["message"]
    assert "fixed incomes" not in result["message"]


def mock_sdk(calls):
    create = AsyncMock(
        side_effect=[
            SimpleNamespace(
                output=[
                    SimpleNamespace(
                        type="function_call", name=name, arguments=json.dumps(args), call_id=str(i)
                    )
                ]
            )
            for i, (name, args) in enumerate(calls)
        ]
    )
    return SimpleNamespace(responses=SimpleNamespace(create=create), close=AsyncMock())


async def test_official_sdk_loop_forwards_fresh_evidence_and_bounded_context(monkeypatch, evidence):
    sdk = mock_sdk(
        [
            ("get_district_profile", {"district_id": "house-30"}),
            ("present_answer", selection().model_dump()),
        ]
    )
    monkeypatch.setattr(agent, "client", lambda: sdk)
    result = await agent.answer(
        ChatRequest(
            message="population here",
            district_id="house-30",
            history=[
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "untrusted previous text"},
            ],
        )
    )
    assert result["citations"][0]["estimate"] == 123
    kwargs = sdk.responses.create.call_args_list[-1].kwargs
    assert kwargs["store"] is False and kwargs["parallel_tool_calls"] is False
    output = next(
        i for i in kwargs["input"] if isinstance(i, dict) and i.get("type") == "function_call_output"
    )
    assert json.loads(output["output"])["facts"][0]["estimate"] == 123
    assert "Latest selected district: house-30" in kwargs["input"][0]["content"]
    sdk.close.assert_awaited_once()


async def test_upstream_failure_is_sanitized_and_client_closed(monkeypatch):
    sdk = SimpleNamespace(
        responses=SimpleNamespace(create=AsyncMock(side_effect=TimeoutError("SECRET credential"))),
        close=AsyncMock(),
    )
    monkeypatch.setattr(agent, "client", lambda: sdk)
    with pytest.raises(agent.AssistantError) as err:
        await agent.answer(ChatRequest(message="population"))
    assert "SECRET" not in err.value.message
    sdk.close.assert_awaited_once()


async def test_invented_evidence_from_model_is_not_displayed(monkeypatch):
    sdk = mock_sdk([("present_answer", selection().model_dump())])
    monkeypatch.setattr(agent, "client", lambda: sdk)
    with pytest.raises(agent.AssistantError):
        await agent.answer(ChatRequest(message="population"))


def test_missing_key_and_invalid_requests_have_explicit_api_states(monkeypatch):
    visits.clear()
    monkeypatch.setattr(agent, "client", lambda: None)
    with TestClient(app) as client:
        r = client.post("/v1/assistant/chat", json={"message": "hello"})
        assert r.status_code == 503 and r.json()["error"]["code"] == "assistant_not_configured"
        assert (
            client.post("/v1/assistant/chat", json={"message": "hi", "district_id": "house-99"}).status_code
            == 422
        )
        assert client.post("/v1/assistant/chat", json={"message": "x" * 21000}).status_code == 413
        assert r.headers["Cache-Control"] == "no-store"
    visits.clear()


def test_chat_rate_limit(monkeypatch):
    visits.clear()
    monkeypatch.setattr(agent, "client", lambda: None)
    with TestClient(app) as client:
        for _ in range(10):
            assert client.post("/v1/assistant/chat", json={"message": "hello"}).status_code == 503
        r = client.post("/v1/assistant/chat", json={"message": "hello"})
        assert r.status_code == 429 and r.headers["Retry-After"] == "60"
    visits.clear()
