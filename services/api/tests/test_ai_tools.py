import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.ai import discovery_agent as module
from app.ai.tools import definitions, dispatch
from app.discovery.dataset_ranker import evaluate
from app.schemas.discovery import Purpose


def test_tool_schemas_are_strict_and_have_no_unregistered_actions():
    tools = definitions()
    assert len(tools) == 7
    for tool in tools:
        assert tool["strict"] is True
        assert tool["parameters"]["additionalProperties"] is False
        assert set(tool["parameters"]["required"]) == set(tool["parameters"]["properties"])
        assert not any(x in tool["name"] for x in ("execute", "approve", "publish"))


async def test_unregistered_tool_cannot_run():
    with pytest.raises(ValueError, match="Unregistered"):
        await dispatch("execute_remote_script", "{}")


async def test_mocked_openai_tool_loop_only_returns_recorded_evidence(monkeypatch, official_house):
    evaluation = evaluate(official_house, Purpose(chamber="house")).model_dump(mode="json")
    function = SimpleNamespace(
        type="function_call",
        name="get_dataset_metadata",
        arguments=json.dumps({"dataset_id": official_house.dataset_id}),
        call_id="testcall",
    )
    final = SimpleNamespace(
        output=[],
        output_text=json.dumps({"dataset_id": official_house.dataset_id, "criteria": ["authority"]}),
    )
    create = AsyncMock(side_effect=[SimpleNamespace(output=[function]), final])
    sdk = SimpleNamespace(responses=SimpleNamespace(create=create), close=AsyncMock())
    monkeypatch.setattr(module, "client", lambda: sdk)
    monkeypatch.setattr(module, "dispatch", AsyncMock(return_value={"verified": True}))
    result = await module.assist("house boundaries", {"evaluations": [evaluation]})
    assert result["enabled"]
    assert result["tool_calls"] == 1
    assert result["evidence_highlights"] == [evaluation["categories"][0]["evidence"]]
    assert create.call_args_list[0].kwargs["store"] is False
    assert sdk.close.await_count == 1


async def test_model_cannot_invent_a_dataset(monkeypatch, official_house):
    sdk = SimpleNamespace(
        responses=SimpleNamespace(
            create=AsyncMock(
                return_value=SimpleNamespace(
                    output=[], output_text='{"dataset_id":"invented","criteria":["authority"]}'
                )
            )
        ),
        close=AsyncMock(),
    )
    monkeypatch.setattr(module, "client", lambda: sdk)
    result = await module.assist("house boundaries", {"evaluations": []})
    assert not result["enabled"]
    assert result["status"] == "unavailable"
