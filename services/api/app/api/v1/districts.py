import json

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import func, select

from app.core.config import ROOT
from app.core.database import session
from app.models.entities import District, Source, Statistic
from app.services import comparison_service
from app.services.district_service import geometry, get_district, list_districts, statistics

router = APIRouter(prefix="/v1", tags=["District intelligence"])


@router.get("/districts")
def districts(chamber: str | None = Query(None, pattern="^(house|senate)$")):
    return list_districts(chamber)


@router.get("/districts/{district_id}")
def district(district_id: str):
    return get_district(district_id)


@router.get("/districts/{district_id}/geometry")
def district_geometry(district_id: str):
    return geometry(district_id)


@router.get("/districts/{district_id}/profile")
@router.get("/districts/{district_id}/demographics")
def profile(district_id: str):
    return {"district": get_district(district_id), "statistics": statistics(district_id)}


@router.get("/districts/{district_id}/indicators/{indicator_code}")
def indicator(district_id: str, indicator_code: str):
    get_district(district_id)
    result = next((s for s in statistics(district_id) if s["indicator"] == indicator_code), None)
    if result is None:
        raise HTTPException(404, "Indicator unavailable for this district")
    return result


@router.get("/indicators")
def indicators():
    from app.analytics.acs import INDICATORS
    from app.analytics.acs_profiles import PROFILE_INDICATORS

    return [{"code": code, **value} for code, value in {**INDICATORS, **PROFILE_INDICATORS}.items()]


@router.get("/districts/{district_id}/compare/state")
def compare_state(district_id: str):
    return comparison_service.compare_state(district_id)


@router.get("/districts/{district_id}/compare/county")
def compare_county(district_id: str):
    return comparison_service.compare_county(district_id)


@router.get("/geography/point-lookup")
def point_lookup(lon: float = Query(ge=-180, le=180), lat: float = Query(ge=-90, le=90)):
    with session() as db:
        point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
        return [
            get_district(d.id)
            for d in db.scalars(select(District).where(func.ST_Covers(District.geom, point)))
        ]


@router.get("/geography/bounds")
def bounds():
    with session() as db:
        return {
            "extent": db.scalar(select(func.ST_AsGeoJSON(func.ST_Envelope(func.ST_Collect(District.geom)))))
        }


@router.get("/geography/layers")
def layers():
    return json.loads((ROOT / "data/manifests/sources.json").read_text())


@router.get("/sources")
def sources():
    with session() as db:
        return [
            {
                "id": s.id,
                "title": s.title,
                "url": s.url,
                "status": s.status,
                "metadata": s.metadata_record,
                "retrieved_at": s.retrieved_at,
            }
            for s in db.scalars(select(Source))
        ]


@router.get("/sources/{source_id}")
def source(source_id: str):
    with session() as db:
        s = db.get(Source, source_id)
        if s is None:
            raise KeyError(source_id)
        return {
            "id": s.id,
            "title": s.title,
            "url": s.url,
            "status": s.status,
            "metadata": s.metadata_record,
            "retrieved_at": s.retrieved_at,
        }


@router.get("/statistics/{statistic_id}/provenance")
def provenance(statistic_id: str):
    with session() as db:
        s = db.get(Statistic, statistic_id)
        if s is None:
            raise KeyError(statistic_id)
        return {
            "statistic_id": s.id,
            "provenance": s.provenance,
            "reference_period": s.reference_period,
            "variables": s.variables,
            "moe": s.moe,
            "method": s.method,
            "source_id": s.source_id,
        }


@router.get("/geography/choropleth")
def choropleth(
    indicator: str = Query(pattern="^(population|median_household_income|poverty_rate)$"),
    chamber: str = Query(pattern="^(house|senate)$"),
):
    with session() as db:
        rows = db.execute(
            select(Statistic, District)
            .join(District, Statistic.geography_id == District.id)
            .where(
                District.chamber == chamber,
                Statistic.indicator == indicator,
                Statistic.reference_period == "2020–2024",
                Statistic.source_id == "acs-2024-5yr",
                Statistic.boundary_vintage == District.vintage,
            )
        ).all()
        values = {d.id: s.estimate for s, d in rows if s.estimate is not None}
        return {
            "indicator": indicator,
            "reference_period": "2020–2024",
            "boundary_vintage": 2022,
            "values": values,
            "unavailable": (51 if chamber == "house" else 25) - len(values),
            "method": "Direct ACS values and documented derived rates; unverified values excluded",
        }


@router.get("/sources/{source_id}/workbooks/{kind}")
def workbook_source(source_id: str, kind: str):
    from app.analytics.acs_profiles import WORKBOOK_FILES as FILES

    SOURCE_ID = "acs-2024-5yr"

    if source_id != SOURCE_ID or kind not in FILES:
        raise HTTPException(404, "Unknown source workbook")
    path = ROOT / "data/raw/acs" / FILES[kind]
    if not path.is_file():
        raise HTTPException(404, "Original source workbook unavailable")
    return FileResponse(
        path,
        filename=path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/geography/districts")
def district_feature_collection(chamber: str = Query(pattern="^(house|senate)$")):
    with session() as db:
        rows = db.execute(
            select(District, func.ST_AsGeoJSON(District.geom))
            .where(District.chamber == chamber)
            .order_by(District.number)
        ).all()
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "objectid": d.number,
                        "id": d.id,
                        "name": d.name,
                        "county": d.county,
                        chamber + "_id": d.number,
                        "boundary_vintage": d.vintage,
                    },
                    "geometry": json.loads(g),
                }
                for d, g in rows
            ],
        }
