from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Dataset(StrictModel):
    dataset_id: str
    title: str
    description: str = ""
    publisher: str | None = None
    provider: str | None = None
    catalog_url: str | None = None
    official_source_url: str | None = None
    service_url: str | None = None
    download_url: str | None = None
    format: str | None = None
    geometry_type: str | None = None
    geographic_coverage: str | None = None
    geographic_level: str | None = None
    geographic_vintage: int | None = None
    reference_year: int | None = None
    publication_date: str | None = None
    modified_date: str | None = None
    license: str | None = None
    keywords: list[str] = Field(default_factory=list)
    feature_count: int | None = None
    available_fields: list[str] = Field(default_factory=list)
    spatial_reference: dict | None = None
    validation_status: str = "catalog_only"
    access_level: str | None = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_metadata: dict = Field(default_factory=dict)
    inspection: dict | None = None


class Purpose(StrictModel):
    chamber: Literal["house", "senate"] | None = None
    geographic_level: str | None = None
    boundary_vintage: int | None = 2022
    required_fields: list[str] = Field(default_factory=list, max_length=30)
    category: Literal["boundary", "statistics", "general"] = "boundary"


class DiscoveryRequest(StrictModel):
    query: str = Field(min_length=3, max_length=500)
    limit: int = Field(default=8, ge=1, le=12)
    purpose: Purpose | None = None
    use_ai: bool = False


class DatasetRequest(StrictModel):
    dataset_id: str = Field(min_length=1, max_length=96, pattern=r"^[a-zA-Z0-9_-]+$")
    purpose: Purpose = Field(default_factory=Purpose)


class EvaluateRequest(StrictModel):
    dataset_ids: list[str] = Field(min_length=1, max_length=12)
    purpose: Purpose = Field(default_factory=Purpose)


class CategoryScore(StrictModel):
    criterion: str
    points: int
    maximum: int
    evidence: str


class Evaluation(StrictModel):
    dataset: Dataset
    score: int
    rubric_version: str = "1.0.0"
    categories: list[CategoryScore]
    status: Literal["rejected", "insufficient_evidence", "valid_candidate", "recommended"]
    positives: list[str]
    limitations: list[str]
    rejections: list[str]
    ingestion_method: str
