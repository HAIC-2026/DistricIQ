from app.schemas.discovery import Evaluation


def plan(evaluation: Evaluation) -> dict:
    d = evaluation.dataset
    return {
        "dataset_id": d.dataset_id,
        "source_url": d.service_url,
        "executable": False,
        "approval_required": True,
        "status": evaluation.status,
        "destination": "PostGIS districts + source registry",
        "required_attributes": [d.inspection.get("identifier_field")] if d.inspection else [],
        "transformations": [
            "Request ArcGIS query outSR=4326",
            "Validate polygon topology; reject invalid geometry",
            "Normalize to MultiPolygon; preserve original capture and checksum",
        ],
        "validations": [
            "Reinspect service and match approved metadata fingerprint",
            "Check chamber, vintage, unique IDs and expected count",
            "Verify exact district number set and Hawaiʻi extent",
            "Atomic transaction; rerun is idempotent",
        ],
        "next_step": "Review evidence, then run the local approve-source CLI. Public API cannot execute ingestion.",
        "limitations": evaluation.rejections + evaluation.limitations,
    }
