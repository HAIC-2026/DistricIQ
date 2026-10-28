"""Bounded read-only program discovery, not a benefit eligibility engine."""

from sqlalchemy import select

from app.core.database import session
from app.models.entities import GovernmentProgram
from app.services.research_service import normalize

TAGS = {
    "snap": "food nutrition low income older families",
    "ssi": "older disability cash retirement low income",
    "aabd": "older disability cash retirement low income",
    "medquest": "health medical insurance low income disability older children",
    "msp": "medicare health insurance older retirement premiums low income",
    "extra-help": "medicare prescription medication older retirement low income",
    "aging-services": "older transportation nutrition meals home care alone disability",
    "kupuna-care": "older disability home care functional needs",
    "hheap": "energy electricity utility bills crisis low income",
    "hcv": "housing rental assistance low income",
    "public-housing": "housing rental assistance low income",
    "affordable-rentals": "housing affordable rental properties older",
    "wic": "nutrition food pregnancy infant children families",
    "tanf": "cash financial families children low income",
    "childcare-subsidy": "childcare children families employment",
    "pod": "preschool children families education tuition",
}


def serialize(program):
    return {
        **program.record,
        "id": program.id,
        "eligibility_status": program.eligibility_status,
        "verification_date": program.verification_date,
        "source_id": program.source_id,
        "provenance_url": "/v1/programs/" + program.id,
        "limitation": "Program information and potential relevance only. Rules remain incomplete; district demographics do not establish individual eligibility. Application route does not guarantee an open waitlist, capacity or approval.",
    }


def search_programs(query, limit=5):
    tokens = set(normalize(query).split()) - {
        "which",
        "what",
        "programs",
        "program",
        "government",
        "existing",
        "might",
        "relevant",
        "support",
        "for",
        "in",
        "my",
        "district",
        "the",
        "are",
        "to",
        "with",
        "and",
    }
    with session() as db:
        ranked = []
        for p in db.scalars(select(GovernmentProgram)):
            text = set(normalize(p.name + " " + p.record["intended_population"]).split())
            tags = set(normalize(TAGS.get(p.id, "")).split())
            score = 5 * len(tokens & text) + 3 * len(tokens & tags)
            if score or not tokens:
                ranked.append((score, p.id, serialize(p)))
        ranked.sort(key=lambda v: (-v[0], v[1]))
        return [p for _, _, p in ranked[:limit]]


def get_program(program_id):
    with session() as db:
        p = db.get(GovernmentProgram, program_id)
        if p is None:
            raise KeyError(program_id)
        return serialize(p)
