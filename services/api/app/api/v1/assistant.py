import asyncio

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from app.ai.district_assistant import AssistantError, answer
from app.core.config import get_settings
from app.schemas.assistant import ChatRequest
from app.services.district_service import get_district

router = APIRouter(prefix="/v1/assistant", tags=["AI Assistant"])
slots = asyncio.Semaphore(2)


@router.get("/status")
def status():
    return {
        "configured": bool(get_settings().openai_api_key.get_secret_value()),
        "model": get_settings().openai_model,
        "reference_period": "2020–2024",
        "history": "Session only; bounded history, no persistent chat database.",
    }


@router.post("/chat")
async def chat(request: ChatRequest):
    if request.district_id:
        await run_in_threadpool(get_district, request.district_id)
    if slots.locked():
        return JSONResponse(
            {"error": {"code": "assistant_busy", "message": "Assistant is busy. Please retry shortly."}},
            status_code=429,
            headers={"Retry-After": "10", "Cache-Control": "no-store"},
        )
    async with slots:
        try:
            return JSONResponse(await answer(request), headers={"Cache-Control": "no-store"})
        except AssistantError as exc:
            return JSONResponse(
                {"error": {"code": exc.code, "message": exc.message}},
                status_code=exc.status,
                headers={"Cache-Control": "no-store"},
            )
