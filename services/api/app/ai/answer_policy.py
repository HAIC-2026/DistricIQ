"""Question/measure compatibility checks, not question-answer templates or generated math."""

import re

from app.services.research_service import normalize


class AnswerMismatch(ValueError):
    """A recoverable tool-selection error; ask the model for compatible evidence."""


def requirements(question):
    q = normalize(question)
    tokens = set(q.split())
    limits = []
    if any(s in q for s in ("fixed income", "primary income")) or tokens & {"primarily", "rely", "relying"}:
        limits.append("joint")
    if any(s in q for s in ("basic necessit", "basic need", "struggle to afford")):
        limits.append("hardship")
    if any(s in q for s in ("instability", "at risk", "eviction", "evicted", "homeless")):
        limits.append("instability")
    if "rest of" in q and "county" in q:
        limits.append("remainder")
    if tokens & {"trend", "trends", "change", "changes", "growth"}:
        limits.append("trends")
    if tokens & {"qualify", "eligible", "eligibility"} or (
        "how many" in q and "benefit" in q and "housing" in q
    ):
        limits.append("eligibility")
    if (
        tokens & {"residents", "people", "older"}
        and tokens & {"rent", "renter", "owner", "own", "occupied", "homeowners", "renters"}
        and "housing" not in q.replace("owner occupied housing", "")
    ):
        limits.append("householder")
    # Broad older-person tenure questions require the explicit householder caveat.
    if tokens & {"older", "65"} and tokens & {"rent", "own", "renter", "owner"}:
        limits.append("householder")
    if "residents" in tokens and "owner occupied" in q:
        limits.append("householder")
    return {
        "income_dependence": "joint" in limits,
        "exhaustive": bool(tokens & {"all", "every", "complete", "comprehensive"}),
        "sex_specific": bool(tokens & {"female", "male", "women", "men"}),
        "older_tenure_comparison": bool(tokens & {"older", "65"})
        and bool(tokens & {"own", "owner", "owners", "homeowners"})
        and bool(tokens & {"rent", "renter", "renters"})
        and not bool(tokens & {"alone", "disability", "disabled"}),
        "limitations": list(dict.fromkeys(limits)),
        "percent": bool(tokens & {"percentage", "percent", "share", "rate"}),
        "severe_rent": bool(tokens & {"severe", "severely"}) and bool(tokens & {"rent", "renter", "renters"}),
        "neighbors": bool(tokens & {"neighboring", "neighbouring", "neighbors", "neighbours"}),
        "income_under_50k": "how many" in q
        and ("50 000" in q or "50000" in q or "50k" in q)
        and bool(tokens & {"less", "under", "below"}),
        "requires_program": bool(tokens & {"program", "programs"})
        or (
            bool(tokens & {"qualify", "eligible", "eligibility"})
            and bool(tokens & {"snap", "ssi", "medicaid", "medicare", "medquest", "aabd", "wic", "tanf"})
        ),
        "count": "how many" in q or "number of" in q,
        "person_request": bool(
            re.search(
                r"(?:how many|number of|percentage of|percent of|share of) (?:all |older |young )?(?:people|residents|individuals|adults|children)\b",
                q,
            )
        ),
        "joint_dimensions": list(dimensions(q))
        if ("how many" in q or bool(tokens & {"percentage", "percent", "share"}))
        and not bool(tokens & {"compare", "compared", "versus", "vs"})
        else [],
    }


def dimensions(text):
    q = normalize(text)
    tokens = set(q.split())
    dims = set()
    if tokens & {"older", "65"}:
        dims.add("age65")
    if tokens & {"child", "children"} or "under 18" in q:
        dims.add("children")
    if "poverty" in tokens:
        dims.add("poverty")
    if "alone" in tokens:
        dims.add("alone")
    if tokens & {"rent", "renter", "renters", "renting", "owner", "own", "owners", "homeowners"}:
        dims.add("tenure")
    if tokens & {"disability", "disabled"}:
        dims.add("disability")
    if "social security" in q and "supplemental security" not in q:
        dims.add("social_security")
    if "snap" in tokens:
        dims.add("snap")
    if "ssi" in tokens or "supplemental security" in q:
        dims.add("ssi")
    return dims


def unsupported_intersection(policy, facts):
    wanted = set(policy.get("joint_dimensions", []))
    if len(wanted) < 2 or not facts:
        return False
    return not any(wanted <= dimensions(f.get("label", "") + " " + f.get("universe", "")) for f in facts)


def person_universe_mismatch(policy, facts):
    return bool(policy.get("person_request")) and any(
        f.get("unit") in {"households", "families", "housing units"}
        or normalize(f.get("universe", "")).startswith(("households ", "families "))
        for f in facts
    )


def check_selection(policy, facts, calls):
    if policy.get("requires_program") and not set(calls) & {"search_programs", "get_program"}:
        raise AnswerMismatch(
            "Retrieve official program-directory information with search_programs or get_program before answering program rules, application or eligibility-input questions."
        )
    codes = {f["indicator"] for f in facts}
    if policy.get("older_tenure_comparison") and facts and not {
        "older_owner_households", "older_renter_households"
    } <= codes:
        raise AnswerMismatch(
            "Use the reviewed older_owner_households and older_renter_households totals for the age-65+ tenure comparison. Separate family/living-arrangement cells do not answer which total is larger. Explain that these count householders, not all older residents."
        )
    if policy.get("income_dependence") and not policy.get("sex_specific") and any(
        code.startswith("B17001_") for code in codes
    ):
        raise AnswerMismatch(
            "A sex-specific or partial age B17001 cell is too narrow for broad older-adult income context. Use the reviewed older_poverty_count or a reported age-65+ poverty rate, alongside income-source context."
        )
    if not policy or not facts or policy.get("limitations"):
        return
    if policy.get("percent") and not any(f["unit"] == "percent" for f in facts):
        raise AnswerMismatch(
            "Retrieve a reported percentage or approved percentage recipe; counts alone do not answer the requested share/rate."
        )
    if policy.get("count") and all(f["unit"] == "percent" for f in facts):
        raise AnswerMismatch(
            "Retrieve a published count or approved count recipe; a rate is not a count. If no count exists, use explicitly labeled context."
        )
    if policy.get("severe_rent") and "B25070_010" not in codes:
        raise AnswerMismatch(
            "Retrieve the published 50%+ gross-rent burden cell through metadata search; 35%+ is not severe burden."
        )
    if policy.get("neighbors") and "compare_neighbors" not in calls:
        raise AnswerMismatch(
            "Use compare_neighbors; consecutive or arbitrarily selected district numbers do not establish spatial adjacency."
        )
    if policy.get("income_under_50k") and not codes & {
        "household_income_under_50000",
        "older_household_income_under_50000",
    }:
        raise AnswerMismatch(
            "Retrieve the reviewed income-under-50000 sum recipe from search_indicators. Separate brackets do not give the requested total."
        )
