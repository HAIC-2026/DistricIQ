import json
from unittest.mock import AsyncMock

import pytest

import app.discovery.arcgis_inspector as module
from app.core.config import ROOT
from app.discovery.arcgis_inspector import ArcGISInspector, InvalidLayer


async def test_real_layer_metadata_and_query_identifiers(monkeypatch):
    data = json.loads((ROOT / "data/fixtures/house.json").read_text())
    ids = json.loads((ROOT / "data/fixtures/house-ids.json").read_text())
    fake = AsyncMock(side_effect=[data, {"count": 51}, ids])
    monkeypatch.setattr(module, "get_json", fake)
    inspector = ArcGISInspector()
    result = await inspector.inspect("https://geodata.hawaii.gov/arcgis/rest/services/AdminBnd/MapServer/33")
    assert result["geographic_vintage"] == 2022
    assert sorted(result["verified_identifiers"]) == list(range(1, 52))
    assert result["spatial_reference"]["latestWkid"] == 3750
    assert fake.call_args_list[2].args[1]["returnGeometry"] == "false"


async def test_missing_fields_is_unavailable(monkeypatch):
    monkeypatch.setattr(module, "get_json", AsyncMock(return_value={"name": "Empty"}))
    with pytest.raises(InvalidLayer):
        await ArcGISInspector().inspect(
            "https://geodata.hawaii.gov/arcgis/rest/services/AdminBnd/MapServer/33"
        )


async def test_service_root_cannot_be_used_as_layer():
    with pytest.raises(ValueError):
        await ArcGISInspector().inspect("https://geodata.hawaii.gov/arcgis/rest/services/AdminBnd/MapServer")
