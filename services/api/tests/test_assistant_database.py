import json
import os

import pytest

from app.ai.district_assistant import render
from app.ai.district_tools import Evidence
from app.schemas.assistant import AnswerSelection

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def seeded():
    if os.getenv("RUN_SEEDED_TESTS") != "1":
        pytest.skip("Requires the existing migrated and populated local database")


def query(name, **arguments):
    e = Evidence()
    result = e.dispatch(name, json.dumps(arguments))
    return e, result


def test_real_house30_answer_and_original_source_cells():
    e, r = query(
        "get_district_indicators",
        district_id="house-30",
        indicators=["population", "median_household_income", "poverty_rate"],
    )
    stats = {s["indicator"]: s for s in r["facts"]}
    assert (stats["population"]["estimate"], stats["population"]["moe"]) == (34283, 1935)
    assert (stats["median_household_income"]["estimate"], stats["median_household_income"]["moe"]) == (
        90180,
        9512,
    )
    assert stats["poverty_rate"]["estimate"] == 9.8
    assert stats["population"]["estimate_cell"] == "DN4"
    result = render(
        AnswerSelection(
            intent="facts",
            fact_refs=list(e.facts),
            comparison_refs=[],
            active_district_id="house-30",
            explanations=[],
        ),
        e,
    )
    assert "34,283 people" in result["message"] and "90% margin of error" in result["message"]
    assert len(result["citations"]) == 3


@pytest.mark.parametrize("benchmark", ["county", "state"])
def test_real_benchmarks_and_calculated_differences(benchmark):
    e, r = query(
        "compare_benchmark", district_id="senate-15", benchmark=benchmark, indicators=["poverty_rate"]
    )
    assert len(r["facts"]) == 2 and len(r["comparisons"]) == 1
    d = r["comparisons"][0]
    left, right = (e.facts[d[k]] for k in ("left_ref", "right_ref"))
    assert left["estimate"] == 8.6
    assert right["geography_id"] == ("county-15003" if benchmark == "county" else "state-15")
    assert d["difference"] == round(left["estimate"] - right["estimate"], 6)
    assert d["unit"] == "percentage points"


def test_real_district_comparison_distribution_housing_and_unavailable():
    e, r = query(
        "compare_districts",
        left_id="house-30",
        right_id="house-31",
        indicators=["poverty_rate", "median_household_income"],
    )
    assert len(r["comparisons"]) == 2
    _, age = query("get_distribution", district_id="house-30", distribution="age", order="largest")
    assert len(age["facts"]) == 13
    assert age["facts"][0]["label"] == "35 to 44 years"
    assert sum(s["estimate"] for s in age["facts"]) == 34283
    _, income = query("get_distribution", district_id="house-30", distribution="income", order="published")
    assert len(income["facts"]) == 10
    _, housing = query("get_housing_statistics", district_id="house-30")
    assert any(s["indicator"] == "median_gross_rent" for s in housing["facts"])
    _, missing = query("explain_available_indicators", district_id="house-30")
    assert len(missing["facts"]) == 2 and all(s["estimate"] is None for s in missing["facts"])
    assert len(missing["supported_indicators"]) == 46
