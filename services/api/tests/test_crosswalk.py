import math

import pytest
from shapely.geometry import box

from app.gis.crosswalk import allocate_counts, area_weights, population_weights, validate_weights


def test_equal_area_intersection_conserves_known_additive_count():
    source = box(-158, 20, -157, 21)
    rows = area_weights(
        {"tract": source},
        {"a": box(-158, 20, -157.5, 21), "b": box(-157.5, 20, -157, 21)},
        justification="Synthetic uniform surface-area count used to validate geographic intersection and conservation.",
    )
    result = allocate_counts(
        {"tract": 100},
        rows,
        statistic_kind="additive_count",
        source_url="fixture:test",
        reference_period="test",
    )
    assert sum(result["estimates"].values()) == pytest.approx(100)
    assert result["estimates"]["a"] == pytest.approx(50, abs=0.01)
    assert result["estimated"]


def test_population_weighted_allocation_uses_verified_blocks():
    rows = population_weights(
        [
            {
                "block_geoid": "1",
                "source_geoid": "t",
                "district_id": "a",
                "population": 30,
                "source_url": "fixture:official",
            },
            {
                "block_geoid": "2",
                "source_geoid": "t",
                "district_id": "b",
                "population": 70,
                "source_url": "fixture:official",
            },
        ]
    )
    result = allocate_counts(
        {"t": 1000}, rows, statistic_kind="additive_count", source_url="fixture:test", reference_period="test"
    )
    assert result["estimates"] == {"a": 300, "b": 700}


@pytest.mark.parametrize("kind", ["median", "percentage", "rate", "ratio"])
def test_nonadditive_statistics_are_rejected(kind):
    with pytest.raises(ValueError, match="Only additive"):
        allocate_counts({}, [], statistic_kind=kind, source_url="x", reference_period="x")


@pytest.mark.parametrize("weight", [0.9, math.nan, math.inf, -0.1, 1.1])
def test_partial_or_invalid_weights_are_rejected(weight):
    with pytest.raises(ValueError):
        validate_weights([{"source_geoid": "t", "district_id": "a", "weight": weight}])


def test_duplicate_weights_rejected():
    with pytest.raises(ValueError):
        validate_weights([{"source_geoid": "t", "district_id": "a", "weight": 0.5}] * 2)


def test_partial_source_coverage_not_renormalized():
    with pytest.raises(ValueError, match="sum to one"):
        area_weights(
            {"t": box(-158, 20, -157, 21)},
            {"a": box(-158, 20, -157.5, 21)},
            justification="Synthetic partial coverage must fail rather than silently renormalize missing geography.",
        )
