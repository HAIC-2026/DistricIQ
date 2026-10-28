"""Developer-only idempotent directory import from reviewed source-discovery records."""

import json
from datetime import date
from urllib.parse import urlsplit

from sqlalchemy import select

from app.core.config import ROOT
from app.core.database import session
from app.models.entities import GovernmentProgram, Source


def ingest():
    path = ROOT / "data/manifests/government-programs.json"
    data = json.loads(path.read_text())
    programs = data["programs"]
    if len(programs) != 16 or len({p["id"] for p in programs}) != 16:
        raise ValueError("Expected reviewed 16-program directory")
    source_id = "government-program-directory-2026-10-26"
    with session() as db, db.begin():
        db.merge(
            Source(
                id=source_id,
                title="Initial official government program directory; rules not fully verified",
                url="https://humanservices.hawaii.gov/",
                status="reviewed_partial",
                metadata_record={
                    "manifest": "data/manifests/government-programs.json",
                    "last_verified": "2026-10-26",
                    "individual_eligibility_supported": False,
                    "official_source_urls": [p["eligibility_url"] for p in programs],
                },
            )
        )
        db.flush()
        for p in programs:
            for field in ("eligibility_url", "application_or_referral_url"):
                u = urlsplit(p[field])
                if u.scheme != "https" or u.username or u.password or not u.hostname:
                    raise ValueError("Invalid official directory URL")
            verified = p["last_verified"][:10]
            date.fromisoformat(verified)
            current = db.get(GovernmentProgram, p["id"])
            if current and current.verification_date > verified:
                raise ValueError(
                    "Refusing to replace newer program verification with an older record"
                )
            db.merge(
                GovernmentProgram(
                    id=p["id"],
                    name=p["name"],
                    agency=p["administering_agency"],
                    source_id=source_id,
                    verification_date=verified,
                    eligibility_status="rules_incomplete",
                    record=p,
                )
            )
        db.flush()
        return {
            "programs": len(list(db.scalars(select(GovernmentProgram)))),
            "individual_eligibility_supported": False,
            "last_verified": "2026-10-26",
        }
