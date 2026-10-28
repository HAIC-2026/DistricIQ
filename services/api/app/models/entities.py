from datetime import datetime, timezone

from geoalchemy2 import Geometry
from sqlalchemy import JSON, CheckConstraint, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def now():
    return datetime.now(timezone.utc)


class Source(Base):
    __tablename__ = "sources"
    id: Mapped[str] = mapped_column(String(96), primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    url: Mapped[str] = mapped_column(String(2048))
    status: Mapped[str] = mapped_column(String(32), default="candidate")
    metadata_record: Mapped[dict] = mapped_column(JSON)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class District(Base):
    __tablename__ = "districts"
    __table_args__ = (
        UniqueConstraint("chamber", "number", "vintage"),
        CheckConstraint("chamber IN ('house','senate')"),
        CheckConstraint(
            "number >= 1 AND ((chamber = 'house' AND number <= 51) OR (chamber = 'senate' AND number <= 25))"
        ),
    )
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    chamber: Mapped[str] = mapped_column(String(10))
    number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    county: Mapped[str | None] = mapped_column(String(50))
    vintage: Mapped[int] = mapped_column(Integer)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"))
    geom = mapped_column(Geometry("MULTIPOLYGON", srid=4326, spatial_index=True), nullable=False)


class Statistic(Base):
    __tablename__ = "statistics"
    __table_args__ = (UniqueConstraint("geography_id", "indicator", "reference_period", "source_id"),)
    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    geography_id: Mapped[str] = mapped_column(String(30), index=True)
    geographic_level: Mapped[str] = mapped_column(String(50))
    boundary_vintage: Mapped[int | None] = mapped_column(Integer)
    indicator: Mapped[str] = mapped_column(String(60), index=True)
    estimate: Mapped[float | None] = mapped_column(Float)
    moe: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(30))
    reference_period: Mapped[str] = mapped_column(String(30))
    variables: Mapped[list] = mapped_column(JSON)
    method: Mapped[str] = mapped_column(String(60), default="direct")
    status: Mapped[str] = mapped_column(String(50), default="available")
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"))
    provenance: Mapped[dict] = mapped_column(JSON)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class EvaluationRecord(Base):
    __tablename__ = "evaluations"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class CrosswalkWeight(Base):
    __tablename__ = "crosswalk_weights"
    __table_args__ = (CheckConstraint("weight >= 0 AND weight <= 1"),)
    source_geoid: Mapped[str] = mapped_column(String(30), primary_key=True)
    district_id: Mapped[str] = mapped_column(ForeignKey("districts.id"), primary_key=True)
    vintage: Mapped[int] = mapped_column(Integer, primary_key=True)
    weight: Mapped[float] = mapped_column(Float)
    method: Mapped[str] = mapped_column(String(50))
    provenance: Mapped[dict] = mapped_column(JSON)


class ACSProfileObservation(Base):
    """All published rows, including suppression markers, kept separately from dashboard aliases."""

    __tablename__ = "acs_profile_observations"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"))
    geography_id: Mapped[str] = mapped_column(String(30), index=True)
    profile: Mapped[str] = mapped_column(String(10))
    row_number: Mapped[int] = mapped_column(Integer)
    definition: Mapped[str] = mapped_column(String(500))
    section: Mapped[str] = mapped_column(String(500))
    estimate: Mapped[float | None] = mapped_column(Float)
    moe: Mapped[float | None] = mapped_column(Float)
    percent: Mapped[float | None] = mapped_column(Float)
    percent_moe: Mapped[float | None] = mapped_column(Float)
    reference_period: Mapped[str] = mapped_column(String(30))
    raw_values: Mapped[dict] = mapped_column(JSON)
    provenance: Mapped[dict] = mapped_column(JSON)
    __table_args__ = (
        UniqueConstraint("geography_id", "profile", "row_number", "reference_period", "source_id"),
    )


class GovernmentProgram(Base):
    """Verified discovery information, explicitly separate from individual eligibility."""

    __tablename__ = "government_programs"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    name: Mapped[str] = mapped_column(String(300))
    agency: Mapped[str] = mapped_column(String(300))
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"))
    verification_date: Mapped[str] = mapped_column(String(10))
    eligibility_status: Mapped[str] = mapped_column(String(50), default="rules_incomplete")
    record: Mapped[dict] = mapped_column(JSON)
