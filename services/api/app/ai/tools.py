from pydantic import Field

from app.discovery.dataset_ranker import evaluate, rank
from app.discovery.dataset_validator import validate
from app.discovery.ingestion_planner import plan
from app.discovery.workflow import workflow
from app.schemas.discovery import DiscoveryRequest, Purpose, StrictModel


class SearchInput(StrictModel):
    query: str = Field(min_length=3, max_length=300)


class DatasetInput(StrictModel):
    dataset_id: str = Field(min_length=1, max_length=96, pattern=r"^[a-zA-Z0-9_-]+$")


class CompareInput(StrictModel):
    dataset_ids: list[str] = Field(min_length=1, max_length=8)
    chamber: str = Field(pattern=r"^(house|senate)$")


TOOLS = {
    "search_geoportal": (SearchInput, "Search verified public catalog metadata."),
    "get_dataset_metadata": (DatasetInput, "Read normalized metadata for a discovered dataset."),
    "inspect_arcgis_layer": (
        DatasetInput,
        "Inspect the service URL recorded by the catalog; no arbitrary URLs.",
    ),
    "compare_datasets": (CompareInput, "Compare deterministic recorded category scores."),
    "rank_datasets": (CompareInput, "Rank with the fixed evidence rubric."),
    "check_geography_compatibility": (CompareInput, "Check geography and boundary compatibility."),
    "prepare_ingestion_plan": (DatasetInput, "Produce a non-executable ingestion plan."),
}


def definitions():
    return [
        {
            "type": "function",
            "name": name,
            "description": description,
            "strict": True,
            "parameters": schema.model_json_schema(),
        }
        for name, (schema, description) in TOOLS.items()
    ]


async def dispatch(name: str, arguments: str):
    if name not in TOOLS:
        raise ValueError("Unregistered tool")
    value = TOOLS[name][0].model_validate_json(arguments)
    if name == "search_geoportal":
        result = await workflow.discover(DiscoveryRequest(query=value.query, limit=5))
        return {"evaluations": result["evaluations"], "warning": result["warning"]}
    if isinstance(value, DatasetInput):
        dataset = await workflow.catalog.get_dataset_metadata(value.dataset_id)
        if name == "get_dataset_metadata":
            return dataset.model_dump(mode="json")
        enriched = await workflow.inspector.enrich(dataset)
        if name == "inspect_arcgis_layer":
            return enriched.model_dump(mode="json")
        return plan(
            evaluate(
                enriched,
                Purpose(
                    chamber=dataset.geographic_level
                    if dataset.geographic_level in ("house", "senate")
                    else None
                ),
            )
        )
    records = [await workflow.catalog.get_dataset_metadata(x) for x in value.dataset_ids]
    records = [await workflow.inspector.enrich(x) for x in records]
    purpose = Purpose(chamber=value.chamber)
    if name == "check_geography_compatibility":
        return {x.dataset_id: validate(x, purpose) for x in records}
    return [x.model_dump(mode="json") for x in rank(records, purpose)]
