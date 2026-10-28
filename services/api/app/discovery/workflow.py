import asyncio
import hashlib
import json
from datetime import datetime, timezone

from app.core.config import get_settings
from app.discovery.arcgis_inspector import ArcGISInspector
from app.discovery.dataset_ranker import rank
from app.discovery.geoportal_client import GeoportalClient
from app.discovery.ingestion_planner import plan
from app.schemas.discovery import DiscoveryRequest, Purpose


class DiscoveryWorkflow:
    def __init__(self):
        self.catalog = GeoportalClient()
        self.inspector = ArcGISInspector()
        self.semaphore = asyncio.Semaphore(3)

    @staticmethod
    def purpose(query: str) -> Purpose:
        text = query.lower()
        chamber = "senate" if "senate" in text else "house" if "house" in text else None
        statistics = any(x in text for x in ("income", "poverty", "population", "rent"))
        return Purpose(chamber=chamber, category="statistics" if statistics else "boundary")

    async def discover(self, request: DiscoveryRequest) -> dict:
        async with self.semaphore:
            purpose = request.purpose or self.purpose(request.query)
            search = f"state {purpose.chamber} districts" if purpose.chamber else request.query
            candidates = await self.catalog.search_datasets(search, request.limit)
            enriched = await asyncio.gather(*(self.inspector.enrich(c) for c in candidates))
            self.catalog._remember(enriched)
            # For statistical requests explicitly evaluate geometry separately. No claim that boundaries contain income.
            scoring_purpose = (
                purpose.model_copy(update={"category": "boundary"})
                if purpose.category == "statistics"
                else purpose
            )
            evaluations = rank(enriched, scoring_purpose)
            recommended = next((e for e in evaluations if e.status == "recommended"), None)
            statistical = None
            if purpose.category == "statistics":
                statistical = {
                    "title": "U.S. Census Bureau 2024 ACS five-year detailed tables",
                    "url": "https://api.census.gov/data/2024/acs/acs5.html",
                    "reference_period": "2020–2024",
                    "guidance": "Prefer direct ACS legislative-district estimates when boundary compatibility is verified. The geometry candidate is for mapping. Never average tract medians.",
                    "availability": "Verify API response, variable and legislative geography before ingestion; no statistical values inferred from catalog metadata.",
                }
            result = {
                "query": request.query,
                "purpose": purpose.model_dump(),
                "mode": self.catalog.mode,
                "warning": self.catalog.warning,
                "evaluations": [e.model_dump(mode="json") for e in evaluations],
                "recommendation": recommended.dataset.dataset_id if recommended else None,
                "explanation": (
                    f"{recommended.dataset.title} is the highest-ranked verified geographic candidate. Review the recorded evidence before approval."
                    if recommended
                    else "No candidate met every required evidence check. Review limitations before choosing a source."
                ),
                "statistical_source": statistical,
                "ingestion_plan": plan(recommended) if recommended else None,
                "ai": {"enabled": False, "status": "not_requested"},
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            result["evaluation_id"] = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()[
                :32
            ]
            directory = get_settings().cache_dir / "evaluations"
            directory.mkdir(parents=True, exist_ok=True)
            (directory / (result["evaluation_id"] + ".json")).write_text(json.dumps(result))
            # Bound local audit storage; explicit CLI exports are retained separately.
            for old in sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime)[:-200]:
                old.unlink(missing_ok=True)
            return result


workflow = DiscoveryWorkflow()
