from fastapi import APIRouter, Query

from app.services.program_service import get_program, search_programs

router = APIRouter(prefix="/v1/programs", tags=["Read-only verified program discovery"])


@router.get("")
def programs(q: str = Query("", max_length=300), limit: int = Query(16, ge=1, le=20)):
    return {"programs": search_programs(q, limit), "individual_eligibility_supported": False}


@router.get("/{program_id}")
def program(program_id: str):
    return get_program(program_id)
