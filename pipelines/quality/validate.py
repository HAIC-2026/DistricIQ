from sqlalchemy import select, text

from app.analytics.acs import INDICATORS
from app.analytics.acs_profiles import PROFILE_INDICATORS
from app.core.database import session
from app.models.entities import District, Statistic


def geography():
    with session() as db:
        rows = list(db.scalars(select(District)))
        for chamber, expected in (("house", 51), ("senate", 25)):
            actual = sorted(d.number for d in rows if d.chamber == chamber)
            if actual != list(range(1, expected + 1)):
                raise ValueError("Missing or duplicate district identifiers")
        invalid = db.scalar(
            text(
                "SELECT count(*) FROM districts WHERE NOT ST_IsValid(geom) OR ST_IsEmpty(geom) OR ST_SRID(geom) <> 4326"
            )
        )
        if invalid:
            raise ValueError("Invalid district geometry")
        if any(d.vintage != 2022 for d in rows):
            raise ValueError("Unexpected boundary plan")
        return {"districts": len(rows), "valid": True}


def statistics():
    with session() as db:
        rows = list(db.scalars(select(Statistic).where(Statistic.source_id == "acs-2024-5yr")))
        if not rows:
            raise ValueError("No ACS data is ingested")
        expected_geographies = 76 + 5 + 1
        is_profiles = all(r.method == "direct_profile_workbook" for r in rows)
        mappings = PROFILE_INDICATORS if is_profiles else INDICATORS
        for code in mappings:
            values = [r for r in rows if r.indicator == code]
            if len(values) != expected_geographies:
                raise ValueError(f"Incomplete ACS coverage for {code}")
        for r in rows:
            if (
                r.reference_period != "2020–2024"
                or (not r.variables and r.estimate is not None)
                or not r.provenance.get("source_url")
            ):
                raise ValueError("Missing statistical provenance")
            if r.estimate is not None and (r.estimate < 0 or (r.unit == "percent" and r.estimate > 100)):
                raise ValueError("Invalid indicator value")
            if r.moe is not None and r.moe < 0:
                raise ValueError("Invalid margin of error")
        return {"statistics": len(rows), "unavailable": sum(r.estimate is None for r in rows), "valid": True}
