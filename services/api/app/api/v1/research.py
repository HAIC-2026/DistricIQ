from fastapi import APIRouter, Query

from app.services import research_service

router = APIRouter(prefix="/v1/research", tags=["Read-only research indicators"])


@router.get("/indicators")
def search(q: str = Query(min_length=2, max_length=300), limit: int = Query(10, ge=1, le=20)):
    return {"indicators": research_service.search(q, limit)}


@router.get("/observations/{geography_id}/{indicator_id}")
def observation(geography_id: str, indicator_id: str):
    try:
        return research_service.observations(geography_id, [indicator_id])[0]
    except ValueError:
        raise KeyError(indicator_id) from None


@router.get("/observations/{geography_id}/{indicator_id}/provenance")
def provenance(geography_id: str, indicator_id: str):
    result = observation(geography_id, indicator_id)
    return {
        "statistic_id": result["id"],
        "indicator": indicator_id,
        "geography_id": geography_id,
        "reference_period": result["reference_period"],
        "source": result["source"],
        "estimate": result["estimate"],
        "moe": result["moe"],
        "unit": result["unit"],
        "universe": result["universe"],
        "method": result["method"],
        "provenance": result["provenance"],
    }
