"""Additive directory for source-backed program discovery; no eligibility decisions."""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"


def upgrade():
    op.create_table(
        "government_programs",
        sa.Column("id", sa.String(80), primary_key=True),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("agency", sa.String(300), nullable=False),
        sa.Column("source_id", sa.String(96), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("verification_date", sa.String(10), nullable=False),
        sa.Column("eligibility_status", sa.String(50), nullable=False),
        sa.Column("record", sa.JSON(), nullable=False),
    )


def downgrade():
    op.drop_table("government_programs")
