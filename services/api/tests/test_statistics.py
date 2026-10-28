import math

import pytest

from app.analytics.acs import calculate, numeric, subset_percentage
from app.core.config import ROOT
from pipelines.dbedt.ingest import parse_population


@pytest.mark.parametrize("value", [None, "null", "-666666666", "-999999999", "NaN", "inf"])
def test_sentinels_not_reported_as_values(value):
    assert numeric(value) is None


def test_original_median_and_moe_preserved():
    result = calculate({"B19013_001E": "71234", "B19013_001M": "5432"}, "median_household_income")
    assert result["estimate"] == 71234
    assert result["moe"] == 5432
    assert result["variables"] == ["B19013_001"]
    assert result["method"] == "direct"


def test_rate_recomputed_from_correct_universe():
    result = calculate(
        {"B17001_002E": "120", "B17001_002M": "20", "B17001_001E": "1000", "B17001_001M": "100"},
        "poverty_rate",
    )
    assert result["estimate"] == 12
    assert result["moe"] == pytest.approx(math.sqrt(400 - 144) / 10)
    assert result["method"] == "derived_subset_percentage"


def test_invalid_denominator_is_unavailable():
    assert subset_percentage(1, 0, 1, 0) == (None, None)
    assert subset_percentage(2, 1, 1, 1) == (None, None)


def test_unavailable_moe_stays_null():
    result = calculate({"B01003_001E": "100", "B01003_001M": "-555555555"}, "population")
    assert result["estimate"] == 100
    assert result["moe"] is None
    assert result["raw_values"]["B01003_001M"] == "-555555555"


def test_actual_dbedt_table_and_combined_maui_geography():
    rows = parse_population((ROOT / "data/fixtures/dbedt-population.xls").read_bytes())
    assert rows[0]["estimate"] == 1446146
    assert sum(r["estimate"] for r in rows[1:]) == rows[0]["estimate"]
    assert rows[-1]["geography_id"] == "county-group-maui-kalawao"
    assert rows[-1]["cell"] == "G26"
