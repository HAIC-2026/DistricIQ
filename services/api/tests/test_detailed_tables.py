import json
import os

import pytest
from sqlalchemy import func, select

from app.core.config import ROOT
from app.core.database import session
from app.models.entities import Source, Statistic
from app.services.research_service import observations
from pipelines.census.detailed import GEO, TABLES, persist_table, specs_from_metadata, validate_rows


def test_parser_rejects_missing_moes_duplicate_headers_and_wrong_geographies():
    # Synthetic metadata/cells, never ingested into the real database.
    metadata = {
        "variables": {
            "B17001_001E": {
                "label": "Estimate!!Total:",
                "concept": TABLES["B17001"],
                "universe": "Population for whom poverty status is determined",
            },
            "B17001_001M": {},
        }
    }
    specs = specs_from_metadata("B17001", metadata)
    good = [
        ["NAME", "GEO_ID", "B17001_001E", "B17001_001M", "state"],
        ["Synthetic unit fixture", "0400000US15", "100", "5", "15"],
    ]
    assert validate_rows("B17001", "state", good, specs)[0]["state"] == "15"
    for invalid in [
        [["NAME", "NAME", "B17001_001E", "B17001_001M", "state"], ["x", "x", "100", "5", "15"]],
        [["NAME", "B17001_001E", "state"], ["x", "100", "15"]],
        [good[0], ["x", "100", "5", "06"]],
        [good[0], good[1], good[1]],
    ]:
        with pytest.raises(ValueError):
            validate_rows("B17001", "state", invalid, specs)


@pytest.mark.integration
class TestOfficialDetailedTables:
    @pytest.fixture(autouse=True)
    def seeded(self):
        if os.getenv("RUN_SEEDED_TESTS") != "1":
            pytest.skip("Requires preserved PostgreSQL and acquired official tables")

    @pytest.mark.parametrize("table", list(TABLES))
    def test_every_native_value_moe_geography_and_provenance_matches_capture(self, table):
        folder = ROOT / "data/raw/acs/2024/detailed" / table
        if not (folder / "state.json").exists():
            pytest.skip("Table not yet acquired")
        with session() as db:
            source = db.get(Source, "acs-2024-detailed-" + table)
            assert source and source.status == "approved"
            metadata = json.loads((folder / "metadata.json").read_text())
            specs = specs_from_metadata(table, metadata)
            actual = {s.id: s for s in db.scalars(select(Statistic).where(Statistic.source_id == source.id))}
            assert len(actual) == len(specs) * 82
            for kind, geo in GEO.items():
                capture = json.loads((folder / (kind + ".json")).read_text())
                rows = validate_rows(table, kind, capture["data"], specs)
                for row in rows:
                    gid = (
                        f"{kind}-{int(row[geo]):02}"
                        if kind in ("house", "senate")
                        else "county-15" + row[geo]
                        if kind == "county"
                        else "state-15"
                    )
                    for variable in specs:
                        stored = actual[f"acs2024-native-{gid}-{variable}"]
                        from app.analytics.acs import numeric

                        assert stored.estimate == numeric(row[variable + "E"])
                        assert stored.moe == numeric(row[variable + "M"])
                        assert stored.provenance["universe"] == specs[variable]["universe"]
                        assert "key" not in stored.provenance["request_parameters"]
                        assert stored.geography_id == gid
                        assert stored.provenance["raw_capture_sha256"] == capture["sha256"]
                        assert stored.provenance["census_geo_id"] == row["GEO_ID"]

    @pytest.mark.parametrize("table", list(TABLES))
    def test_reimport_is_idempotent_and_preserves_workbooks(self, table):
        folder = ROOT / "data/raw/acs/2024/detailed" / table
        if not (folder / "state.json").exists():
            pytest.skip("B17001 not acquired")
        metadata = json.loads((folder / "metadata.json").read_text())
        captures = {kind: json.loads((folder / (kind + ".json")).read_text()) for kind in GEO}
        before = observations("house-30", [table + "_001"])
        assert persist_table(table, metadata, captures)["records"] == 82 * len(
            specs_from_metadata(table, metadata)
        )
        after = observations("house-30", [table + "_001"])
        assert [r["estimate"] for r in before] == [r["estimate"] for r in after]
        with session() as db:
            assert (
                db.scalar(
                    select(func.count()).select_from(Statistic).where(Statistic.source_id == "acs-2024-5yr")
                )
                == 3772
            )
        assert after[0]["estimate"] > 0
