import json
from unittest.mock import AsyncMock

import pytest

import app.discovery.geoportal_client as module
from app.core.config import ROOT, Settings
from app.core.http import UpstreamUnavailable
from app.discovery.geoportal_client import GeoportalClient, normalize


def test_real_dcat_parser_preserves_null_reference_year_and_raw():
    raw = json.loads((ROOT / "data/fixtures/dcat-snapshot.json").read_text())["data"]["dataset"][0]
    d = normalize(raw)
    assert d.raw_metadata == raw
    assert d.reference_year is None
    assert d.publisher
    assert "<" not in d.description


async def test_documented_pagination_and_duplicate_services(monkeypatch):
    features = json.loads((ROOT / "data/fixtures/dcat-snapshot.json").read_text())["data"]["dataset"]
    raw = next(r for r in features if r["title"] == "Hawaii State House Districts 2022")
    search = {"id": "test", "properties": {"title": raw["title"], "url": raw["distribution"][1]["accessURL"]}}
    other = {
        "id": "other",
        "properties": {
            "title": "Other",
            "url": "https://geodata.hawaii.gov/arcgis/rest/services/AdminBnd/MapServer/34",
        },
    }
    fake = AsyncMock(
        side_effect=[
            {"features": [search, search], "numberMatched": 3, "numberReturned": 2},
            {"features": [other], "numberMatched": 3, "numberReturned": 1},
        ]
    )
    monkeypatch.setattr(module, "get_json", fake)
    client = GeoportalClient()
    rows = await client.search_datasets("districts", 3)
    assert len(rows) == 2
    assert fake.call_args_list[1].args[1]["startindex"] == 3
    assert fake.call_args_list[0].args[0].endswith("/collections/dataset/items")


async def test_cached_dcat_fallback_and_retrieval_timestamp(monkeypatch, tmp_path):
    settings = Settings(cache_dir=tmp_path, cache_ttl_seconds=0)
    monkeypatch.setattr(module, "get_settings", lambda: settings)
    envelope = json.loads((ROOT / "data/fixtures/dcat-snapshot.json").read_text())
    (tmp_path / "dcat.json").write_text(json.dumps(envelope))
    monkeypatch.setattr(module, "get_json", AsyncMock(side_effect=UpstreamUnavailable("outage")))
    client = GeoportalClient()
    rows = await client.search_datasets("house districts", 8)
    assert rows
    assert client.mode == "stale_dcat"
    assert client.warning
    assert rows[0].retrieved_at.isoformat() == envelope["retrieved_at"]


async def test_no_cache_and_outage_returns_unavailable(monkeypatch, tmp_path):
    monkeypatch.setattr(module, "get_settings", lambda: Settings(cache_dir=tmp_path))
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "get_json", AsyncMock(side_effect=UpstreamUnavailable("outage")))
    with pytest.raises(UpstreamUnavailable, match="no catalog snapshot"):
        await GeoportalClient().search_datasets("housing", 5)


async def test_retrieval_by_id_and_distributions(monkeypatch, tmp_path):
    envelope = json.loads((ROOT / "data/fixtures/dcat-snapshot.json").read_text())
    monkeypatch.setattr(module, "get_settings", lambda: Settings(cache_dir=tmp_path))
    monkeypatch.setattr(module, "get_json", AsyncMock(return_value=envelope["data"]))
    c = GeoportalClient()
    records = await c.list_catalog_datasets()
    assert len(records) > 300
    r = await c.get_dataset_metadata(records[0].dataset_id)
    assert r.title == records[0].title
    assert await c.get_dataset_distributions(r.dataset_id)
