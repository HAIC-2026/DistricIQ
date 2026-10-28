"""Real geometry conservation example: allocation of polygon surface area, not residents."""

import json

from pyproj import Transformer
from shapely import segmentize
from shapely import transform as transform_coordinates
from shapely.geometry import shape

from app.core.config import ROOT
from app.gis.crosswalk import HAWAII_ALBERS, allocate_counts, area_weights


def run():
    sources = {}
    targets = {}
    for chamber, destination in (("house", sources), ("senate", targets)):
        path = ROOT / f"data/raw/geography/{chamber}-2022.geojson"
        data = json.loads(path.read_text())
        for f in data["features"]:
            destination[f"{chamber}-{int(f['properties'][chamber + '_id']):02}"] = shape(f["geometry"])
    weights = area_weights(
        sources,
        targets,
        justification="Allocate polygon surface area itself; area density is exactly one square metre per square metre. No population or demographic allocation is made.",
    )
    project = Transformer.from_crs("EPSG:4326", HAWAII_ALBERS, always_xy=True).transform
    counts = {
        k: transform_coordinates(segmentize(g, 0.0025), project, interleaved=False).area
        for k, g in sources.items()
    }
    result = allocate_counts(
        counts,
        weights,
        statistic_kind="additive_count",
        source_url="https://geodata.hawaii.gov/arcgis/rest/services/AdminBnd/MapServer",
        reference_period="2022 boundary plan",
    )
    errors = {
        k: abs(
            result["estimates"].get(k, 0)
            - transform_coordinates(segmentize(g, 0.0025), project, interleaved=False).area
        )
        / transform_coordinates(segmentize(g, 0.0025), project, interleaved=False).area
        for k, g in targets.items()
    }
    if max(errors.values()) > 0.0001:
        raise ValueError("Crosswalk area benchmark differs from directly measured target area")
    result.update(
        {
            "indicator": "boundary_polygon_surface_area_m2",
            "benchmark_max_relative_error": max(errors.values()),
            "limitation": "Demonstrates actual spatial intersection and conservation, not demographic apportionment.",
        }
    )
    output = ROOT / "data/processed/crosswalk-area-validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2))
    return {"weights": len(weights), "conserved": True, "max_relative_error": max(errors.values())}
