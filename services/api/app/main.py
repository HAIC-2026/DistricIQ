import time
from collections import defaultdict, deque

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.assistant import router as assistant_router
from app.api.v1.discovery import router as discovery_router
from app.api.v1.districts import router as district_router
from app.api.v1.programs import router as program_router
from app.api.v1.research import router as research_router
from app.core.config import get_settings
from app.core.database import engine
from app.core.http import UpstreamUnavailable

app = FastAPI(
    title="DistrictIQ Hawaiʻi",
    version="0.1.0",
    description="Verified geographic data discovery and district intelligence",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins.split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    allow_credentials=False,
)
visits = defaultdict(deque)


@app.middleware("http")
async def bounds(request: Request, call_next):
    if request.method == "POST":
        try:
            length = int(request.headers.get("content-length", "0") or 0)
        except ValueError:
            return JSONResponse(
                {"error": {"code": "invalid_length", "message": "Invalid Content-Length"}}, status_code=400
            )
        if length < 0 or length > 20000:
            return JSONResponse(
                {"error": {"code": "too_large", "message": "Request body exceeds limit"}}, status_code=413
            )
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 20000:
                return JSONResponse(
                    {"error": {"code": "too_large", "message": "Request body exceeds limit"}}, status_code=413
                )
        request._body = bytes(body)
    is_chat = request.url.path == "/v1/assistant/chat" and request.method == "POST"
    if request.url.path.startswith("/v1/discovery") or is_chat:
        # Single-process development limit; deployment must also enforce an edge limit.
        host = request.client.host if request.client else "unknown"
        key = ("assistant:" if is_chat else "discovery:") + host
        now = time.monotonic()
        queue = visits[key]
        while queue and queue[0] < now - 60:
            queue.popleft()
        limit = 10 if is_chat else 30
        if len(queue) >= limit:
            return JSONResponse(
                {
                    "error": {
                        "code": "rate_limited",
                        "message": f"Request limit: {limit} per minute. Please retry shortly.",
                    }
                },
                status_code=429,
                headers={"Retry-After": "60"},
            )
        queue.append(now)
        if len(visits) > 5000:
            for host in list(visits):
                if not visits[host] or visits[host][-1] < now - 60:
                    del visits[host]
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    return JSONResponse(
        {
            "error": {
                "code": "invalid_request",
                "message": "Request parameters failed validation",
                "fields": [list(e["loc"]) for e in exc.errors()],
            }
        },
        status_code=422,
    )


@app.exception_handler(StarletteHTTPException)
async def http_error(request, exc):
    return JSONResponse(
        {"error": {"code": "http_error", "message": str(exc.detail)}}, status_code=exc.status_code
    )


@app.exception_handler(UpstreamUnavailable)
async def unavailable(request, exc):
    return JSONResponse({"error": {"code": "source_unavailable", "message": str(exc)}}, status_code=503)


@app.exception_handler(SQLAlchemyError)
async def database_error(request, exc):
    return JSONResponse(
        {
            "error": {
                "code": "database_unavailable",
                "message": "PostGIS data store is unavailable. Start PostgreSQL, migrate and ingest approved sources.",
            }
        },
        status_code=503,
    )


@app.exception_handler(KeyError)
async def not_found(request, exc):
    return JSONResponse({"error": {"code": "not_found", "message": "Record not found"}}, status_code=404)


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "service": "districtiq-api",
        "ai_configured": bool(get_settings().openai_api_key.get_secret_value()),
    }


@app.get("/readyz")
def ready():
    try:
        with engine().connect() as db:
            db.execute(text("SELECT PostGIS_Version()"))
            db.execute(text("SELECT version_num FROM alembic_version"))
        return {"status": "ready", "database": "postgresql", "postgis": True}
    except SQLAlchemyError:
        return JSONResponse(
            {"status": "not_ready", "database": "unavailable_or_unmigrated", "discovery_available": True},
            status_code=503,
        )


app.include_router(discovery_router)
app.include_router(district_router)
app.include_router(assistant_router)
app.include_router(research_router)
app.include_router(program_router)
