"""Explicit allocation only. No median, percentage, rate, or ratio can be allocated as a count."""

import math
from collections import defaultdict

from pyproj import Transformer
from shapely import segmentize
from shapely import transform as transform_coordinates

# Hawaiʻi Albers equal-area; input/output geometries are WGS84.
HAWAII_ALBERS = "+proj=aea +lat_1=8 +lat_2=18 +lat_0=13 +lon_0=-157 +datum=NAD83 +units=m +no_defs"


def area_weights(sources: dict, districts: dict, *, justification: str) -> list[dict]:
    if len(justification.strip()) < 30:
        raise ValueError("An explicit area-weighting justification is required")
    project = Transformer.from_crs("EPSG:4326", HAWAII_ALBERS, always_xy=True).transform
    target = {
        k: transform_coordinates(segmentize(g, 0.0025), project, interleaved=False)
        for k, g in districts.items()
    }
    rows = []
    for geoid, geom in sources.items():
        if geom.is_empty or not geom.is_valid:
            raise ValueError("Invalid source geometry")
        source = transform_coordinates(segmentize(geom, 0.0025), project, interleaved=False)
        if source.area <= 0:
            raise ValueError("Nonpositive source area")
        for district, polygon in target.items():
            if not polygon.is_valid:
                raise ValueError("Invalid district geometry")
            weight = source.intersection(polygon).area / source.area
            if weight > 1e-12:
                rows.append(
                    {
                        "source_geoid": geoid,
                        "district_id": district,
                        "weight": weight,
                        "method": "area_weighted",
                        "justification": justification,
                    }
                )
    validate_weights(rows)
    return rows


def population_weights(blocks: list[dict]) -> list[dict]:
    """Blocks must already be assigned using an official relationship or verified point/polygon join.
    Require unsplit blocks; split-block population cannot be guessed from area.
    """
    totals = defaultdict(float)
    cells = defaultdict(float)
    seen = set()
    for block in blocks:
        if block["block_geoid"] in seen or block.get("split", False):
            raise ValueError("Duplicate or split block requires an official allocation relationship")
        seen.add(block["block_geoid"])
        population = block["population"]
        if not math.isfinite(population) or population < 0 or not block.get("source_url"):
            raise ValueError("Verified nonnegative block population and source are required")
        totals[block["source_geoid"]] += population
        cells[(block["source_geoid"], block["district_id"])] += population
    rows = []
    for (source, district), population in cells.items():
        if totals[source] <= 0:
            raise ValueError("Cannot population-weight an empty source geography")
        rows.append(
            {
                "source_geoid": source,
                "district_id": district,
                "weight": population / totals[source],
                "method": "block_population_weighted",
            }
        )
    validate_weights(rows)
    return rows


def validate_weights(rows: list[dict], tolerance: float = 1e-5):
    totals = defaultdict(float)
    pairs = set()
    for row in rows:
        pair = row["source_geoid"], row["district_id"]
        w = row["weight"]
        if pair in pairs or not math.isfinite(w) or not 0 <= w <= 1 + tolerance:
            raise ValueError("Invalid, duplicate, or nonfinite crosswalk weight")
        pairs.add(pair)
        totals[pair[0]] += w
    if not totals or any(abs(total - 1) > tolerance for total in totals.values()):
        raise ValueError("Source weights must sum to one; partial coverage cannot be silently normalized")


def allocate_counts(
    counts: dict[str, float],
    weights: list[dict],
    *,
    statistic_kind: str,
    source_url: str,
    reference_period: str,
) -> dict:
    if statistic_kind != "additive_count":
        raise ValueError(
            "Only additive counts can be allocated. Recompute rates from compatible counts; never average medians."
        )
    if not source_url or not reference_period:
        raise ValueError("Source and reference period are required")
    validate_weights(weights)
    if set(counts) != {w["source_geoid"] for w in weights}:
        raise ValueError("Counts and crosswalk geographies must match exactly")
    if any(not math.isfinite(x) or x < 0 for x in counts.values()):
        raise ValueError("Counts must be finite and nonnegative")
    result = defaultdict(float)
    for row in weights:
        result[row["district_id"]] += counts[row["source_geoid"]] * row["weight"]
    if not math.isclose(sum(result.values()), sum(counts.values()), rel_tol=1e-5, abs_tol=1e-5):
        raise ValueError("Allocation did not conserve the source total")
    return {
        "estimates": dict(result),
        "estimated": True,
        "source_url": source_url,
        "reference_period": reference_period,
        "weights": weights,
        "uncertainty": "Allocation adds model uncertainty not represented by a survey MOE. No precision claim.",
    }
