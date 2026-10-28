import json

from fastapi import APIRouter, HTTPException, Query

from app.ai.discovery_agent import assist
from app.core.config import get_settings
from app.discovery.dataset_ranker import evaluate, rank
from app.discovery.ingestion_planner import plan
from app.discovery.workflow import workflow
from app.schemas.discovery import DatasetRequest, DiscoveryRequest, EvaluateRequest

router = APIRouter(prefix="/v1/discovery", tags=["Discovery"])


@router.get("/search")
async def search(q: str = Query(min_length=3, max_length=500), limit: int = Query(8, ge=1, le=12)):
    return await workflow.discover(DiscoveryRequest(query=q, limit=limit))


@router.get("/datasets/{dataset_id}")
async def dataset(dataset_id: str):
    try:
        record = await workflow.catalog.get_dataset_metadata(dataset_id)
        return await workflow.inspector.enrich(record)
    except KeyError:
        raise HTTPException(404, "Dataset not found in verified catalog") from None


@router.post("/evaluate")
async def evaluate_datasets(request: EvaluateRequest):
    try:
        datasets = [await workflow.catalog.get_dataset_metadata(x) for x in request.dataset_ids]
        datasets = [await workflow.inspector.enrich(x) for x in datasets]
        return rank(datasets, request.purpose)
    except KeyError:
        raise HTTPException(404, "Unknown dataset") from None


@router.post("/recommend")
async def recommend(request: DiscoveryRequest):
    result = await workflow.discover(request)
    if request.use_ai:
        result["ai"] = await assist(request.query, result)
    return result


@router.post("/ingestion-plan")
async def ingestion_plan(request: DatasetRequest):
    try:
        dataset = await workflow.inspector.enrich(
            await workflow.catalog.get_dataset_metadata(request.dataset_id)
        )
        return plan(evaluate(dataset, request.purpose))
    except KeyError:
        raise HTTPException(404, "Unknown dataset") from None


@router.get("/evaluations")
def evaluations():
    directory = get_settings().cache_dir / "evaluations"
    paths = sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:20]
    return {"audit_store": "local_metadata_cache", "evaluations": [json.loads(p.read_text()) for p in paths]}
