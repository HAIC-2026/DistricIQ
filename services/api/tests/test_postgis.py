import os

import pytest
from sqlalchemy import text

from app.core.database import engine

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def require_explicit_integration_database():
    if os.getenv("RUN_POSTGIS_TESTS") != "1":
        pytest.skip("Set RUN_POSTGIS_TESTS=1 against a migrated disposable database")


def test_database_postgis_migration_and_spatial_predicate():
    with engine().connect() as db:
        assert db.scalar(text("SELECT PostGIS_Version()"))
        assert db.scalar(text("SELECT version_num FROM alembic_version")) == "0003"
        assert db.scalar(
            text(
                "SELECT ST_Covers(ST_MakeEnvelope(-158,20,-157,21,4326),ST_SetSRID(ST_Point(-157.5,20.5),4326))"
            )
        )
        assert db.scalar(
            text(
                "SELECT abs(ST_X(ST_Transform(ST_Transform(ST_SetSRID(ST_Point(-157.8,21.3),4326),3750),4326)) + 157.8) < 0.00001"
            )
        )
