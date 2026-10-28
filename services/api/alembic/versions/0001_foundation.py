"""Frozen initial schema: registry, districts, statistical provenance, audit and crosswalks."""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

revision = "0001"
down_revision = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.create_table(
        "sources",
        sa.Column("id", sa.String(96), primary_key=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("metadata_record", sa.JSON(), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "districts",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("chamber", sa.String(10), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("county", sa.String(50)),
        sa.Column("vintage", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(96), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("geom", Geometry("MULTIPOLYGON", srid=4326, spatial_index=False), nullable=False),
        sa.UniqueConstraint("chamber", "number", "vintage"),
        sa.CheckConstraint("chamber IN ('house','senate')"),
        sa.CheckConstraint(
            "number >= 1 AND ((chamber = 'house' AND number <= 51) OR (chamber = 'senate' AND number <= 25))"
        ),
    )
    op.create_index("idx_districts_geom", "districts", ["geom"], postgresql_using="gist")
    op.create_table(
        "statistics",
        sa.Column("id", sa.String(120), primary_key=True),
        sa.Column("geography_id", sa.String(30), nullable=False),
        sa.Column("geographic_level", sa.String(50), nullable=False),
        sa.Column("boundary_vintage", sa.Integer()),
        sa.Column("indicator", sa.String(60), nullable=False),
        sa.Column("estimate", sa.Float()),
        sa.Column("moe", sa.Float()),
        sa.Column("unit", sa.String(30), nullable=False),
        sa.Column("reference_period", sa.String(30), nullable=False),
        sa.Column("variables", sa.JSON(), nullable=False),
        sa.Column("method", sa.String(60), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("source_id", sa.String(96), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("provenance", sa.JSON(), nullable=False),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("geography_id", "indicator", "reference_period", "source_id"),
    )
    op.create_index("ix_statistics_geography_id", "statistics", ["geography_id"])
    op.create_index("ix_statistics_indicator", "statistics", ["indicator"])
    op.create_table(
        "evaluations",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "crosswalk_weights",
        sa.Column("source_geoid", sa.String(30), primary_key=True),
        sa.Column("district_id", sa.String(20), sa.ForeignKey("districts.id"), primary_key=True),
        sa.Column("vintage", sa.Integer(), primary_key=True),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("method", sa.String(50), nullable=False),
        sa.Column("provenance", sa.JSON(), nullable=False),
        sa.CheckConstraint("weight >= 0 AND weight <= 1"),
    )


def downgrade():
    for name in ("crosswalk_weights", "evaluations", "statistics", "districts", "sources"):
        op.drop_table(name)
