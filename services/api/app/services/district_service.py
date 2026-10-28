from sqlalchemy import func, select

from app.core.database import session
from app.models.entities import District, Source, Statistic


def district_dict(d: District):
    return {
        "id": d.id,
        "chamber": d.chamber,
        "number": d.number,
        "name": d.name,
        "county": d.county,
        "boundary_vintage": d.vintage,
        "source_id": d.source_id,
    }


def list_districts(chamber: str | None = None):
    with session() as db:
        query = select(District).order_by(District.chamber, District.number)
        if chamber:
            query = query.where(District.chamber == chamber)
        return [district_dict(x) for x in db.scalars(query)]


def get_district(district_id: str):
    with session() as db:
        d = db.get(District, district_id)
        if d is None:
            raise KeyError(district_id)
        return district_dict(d)


def geometry(district_id: str):
    import json

    with session() as db:
        geom = db.scalar(select(func.ST_AsGeoJSON(District.geom)).where(District.id == district_id))
        if geom is None:
            raise KeyError(district_id)
        return {"type": "Feature", "properties": get_district(district_id), "geometry": json.loads(geom)}


def statistics(geography_id: str):
    with session() as db:
        rows = db.execute(
            # Preserve the dashboard contract. Native research cells use the research API/tools.
            select(Statistic, Source)
            .join(Source)
            .where(Statistic.geography_id == geography_id, ~Source.id.like("acs-2024-detailed-%"))
        ).all()
        return [
            {
                "id": x.id,
                "indicator": x.indicator,
                "label": x.provenance.get("variable_definition", x.indicator.replace("_", " ")),
                "display_group": x.provenance.get("display_group"),
                "display_order": x.provenance.get("display_order", 0),
                "estimate": x.estimate,
                "moe": x.moe,
                "unit": x.unit,
                "reference_period": x.reference_period,
                "geographic_level": x.geographic_level,
                "boundary_vintage": x.boundary_vintage,
                "variables": x.variables,
                "method": x.method,
                "status": x.status,
                "source": {"id": s.id, "title": s.title, "url": s.url},
                "provenance": x.provenance,
                "ingested_at": x.ingested_at,
            }
            for x, s in rows
        ]
