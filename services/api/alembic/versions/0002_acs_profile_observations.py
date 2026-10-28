"""Retain each original DP02–DP05 row and its four reported measures."""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"


def upgrade():
    op.create_table(
        "acs_profile_observations",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("source_id", sa.String(96), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("geography_id", sa.String(30), nullable=False),
        sa.Column("profile", sa.String(10), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("definition", sa.String(500), nullable=False),
        sa.Column("section", sa.String(500), nullable=False),
        sa.Column("estimate", sa.Float()),
        sa.Column("moe", sa.Float()),
        sa.Column("percent", sa.Float()),
        sa.Column("percent_moe", sa.Float()),
        sa.Column("reference_period", sa.String(30), nullable=False),
        sa.Column("raw_values", sa.JSON(), nullable=False),
        sa.Column("provenance", sa.JSON(), nullable=False),
        sa.UniqueConstraint("geography_id", "profile", "row_number", "reference_period", "source_id"),
    )
    op.create_index("ix_acs_profile_observations_geography_id", "acs_profile_observations", ["geography_id"])


def downgrade():
    op.drop_table("acs_profile_observations")
