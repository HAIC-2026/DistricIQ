"""Read-only metadata search, original profile access and reviewed statistical recipes."""

import math
import re
import unicodedata

from sqlalchemy import func, select

from app.analytics.acs import subset_percentage
from app.analytics.acs_profiles import PROFILE_INDICATORS
from app.analytics.research_indicators import DERIVED, RAW
from app.core.database import session
from app.models.entities import ACSProfileObservation, District, Source, Statistic
from app.services.district_service import get_district, statistics

PERIOD = "2020–2024"


def normalize(text):
    text = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    aliases = {
        "kupuna": "older",
        "seniors": "older",
        "elderly": "older",
        "bachelors": "bachelor",
        "education": "educational",
        "disabilities": "disability",
        "renters": "renter",
        "homeowners": "owner",
        "grandkids": "grandchildren",
    }
    return " ".join(aliases.get(t, t) for t in text.split())


def catalog(*, native=True):
    result = {
        k: {
            "code": k,
            "label": v["label"],
            "unit": v["unit"],
            "universe": legacy_universe(k),
            "keywords": k.replace("_", " "),
            "source_id": "acs-2024-5yr",
            "reference_period": PERIOD,
            "method": "reported",
        }
        for k, v in PROFILE_INDICATORS.items()
    }
    result.update(RAW)
    result.update(
        {
            k: {
                "code": k,
                "source_id": "acs-2024-5yr",
                "reference_period": PERIOD,
                "method": "calculated",
                **v,
            }
            for k, v in DERIVED.items()
        }
    )
    if native:
        with session() as db:
            for src in db.scalars(
                select(Source).where(Source.status == "approved", Source.id.like("acs-2024-detailed-%"))
            ):
                result.update(src.metadata_record.get("indicators", {}))
    result.update(native_recipes(result))
    if "B25070_010" in result and "50.0 percent or more" in result["B25070_010"]["label"]:
        result["B25070_010"] = {
            **result["B25070_010"],
            "label": "Cash-rent households spending 50% or more of income on gross rent (severe cost burden)",
            "keywords": "severe severely burdened renters rent housing affordability 50 percent",
        }
    return result


def legacy_universe(code):
    if code in {"poverty_rate", "poverty_population", "poverty_denominator"}:
        return "Population for whom poverty status is determined; not all residents"
    if code.startswith("rent_burden"):
        return "Renter-occupied units with computable gross-rent / household-income share"
    if code.startswith("unmortgaged_burden"):
        return "Owner-occupied units without a mortgage and with computable owner-cost share"
    if code.startswith("mortgage_burden"):
        return "Owner-occupied units with a mortgage and with computable owner-cost share"
    if code == "median_gross_rent":
        return "Renter-occupied housing units paying cash rent; monthly gross rent"
    if code == "median_household_income" or code.startswith("income_profile"):
        return "Households; annual income in 2024 inflation-adjusted dollars"
    if code in {"households", "owner_occupied", "renter_occupied"}:
        return "Households (occupied housing units), not individual residents"
    if code == "total_housing_units":
        return "All housing units, occupied and vacant"
    return "Total resident population"


def native_recipes(definitions):
    """Only expose combinations whose exact source cells are imported and label-checked."""
    recipes = {}
    if "B17001_059" in definitions:
        for code, label, indices in [
            ("older_poverty_count", "People 65+ below poverty", [15, 16, 29, 30]),
            ("child_poverty_count", "Children under 18 below poverty", [*range(4, 10), *range(18, 24)]),
        ]:
            inputs = [f"B17001_{i:03}" for i in indices]
            if all("below poverty level" in definitions[i]["label"] for i in inputs):
                recipes[code] = {
                    "code": code,
                    "label": label,
                    "unit": "people",
                    "universe": "Population for whom poverty status is determined; "
                    + ("age 65+" if code.startswith("older") else "under 18"),
                    "inputs": inputs,
                    "operation": "sum",
                    "source_id": "acs-2024-detailed-B17001",
                    "reference_period": PERIOD,
                    "method": "calculated",
                    "keywords": "poverty children older kupuna count below income",
                }
    if "B25007_021" in definitions:
        for code, label, indices in [
            ("older_owner_households", "Owner households with householder 65+", [9, 10, 11]),
            ("older_renter_households", "Renter households with householder 65+", [19, 20, 21]),
        ]:
            inputs = [f"B25007_{i:03}" for i in indices]
            if all(
                any(age in definitions[i]["label"] for age in ("65 to 74", "75 to 84", "85 years and over"))
                for i in inputs
            ):
                recipes[code] = {
                    "code": code,
                    "label": label,
                    "unit": "households",
                    "universe": "Occupied households with householder 65+; not all individual residents age 65+",
                    "inputs": inputs,
                    "operation": "sum",
                    "source_id": "acs-2024-detailed-B25007",
                    "reference_period": PERIOD,
                    "method": "calculated",
                    "keywords": "older kupuna owner renter tenure housing",
                }
    if "B19037_062" in definitions:
        inputs = [f"B19037_{i:03}" for i in range(54, 63)]
        if all("Householder 65 years and over" in definitions[i]["label"] for i in inputs):
            recipes["older_household_income_under_50000"] = {
                "code": "older_household_income_under_50000",
                "label": "Households headed by a person 65+ with annual household income below $50,000 (2024 dollars)",
                "unit": "households",
                "universe": "Households with householder 65+; household income, not individual income or primary benefit dependence",
                "inputs": inputs,
                "operation": "sum",
                "source_id": "acs-2024-detailed-B19037",
                "reference_period": PERIOD,
                "method": "calculated",
                "keywords": "older kupuna household income 50000 low below retirement",
            }
    return recipes


def search(query, limit=10):
    tokens = set(normalize(query).split()) - {
        "what",
        "how",
        "many",
        "in",
        "my",
        "the",
        "is",
        "are",
        "a",
        "this",
        "district",
        "of",
        "with",
        "and",
        "do",
        "does",
        "here",
        "percentage",
        "number",
    }
    found = []
    for code, spec in catalog().items():
        label = set(normalize(spec["label"]).split())
        universe = set(normalize(spec["universe"]).split())
        tags = set(normalize(spec.get("keywords", "")).split())
        score = 5 * len(tokens & label) + 2 * len(tokens & universe) + len(tokens & tags)
        if normalize(query) == normalize(code):
            score += 100
        if score:
            found.append((score, code, spec))
    found.sort(key=lambda x: (-x[0], x[1]))
    return [{**spec, "score": score} for score, _, spec in found[:limit]]


def validate_geography(geo):
    if geo.startswith(("house-", "senate-")):
        get_district(geo)
    elif geo not in {"state-15", *["county-15" + x for x in ("001", "003", "005", "007", "009")]}:
        raise ValueError("Unsupported geography")


def neighbors(district_id):
    district = get_district(district_id)
    with session() as db:
        target = select(District.geom).where(District.id == district_id).scalar_subquery()
        # Rook adjacency: a shared boundary longer than one projected metre; point contacts excluded.
        ids = list(
            db.scalars(
                select(District.id)
                .where(
                    District.chamber == district["chamber"],
                    District.vintage == 2022,
                    District.id != district_id,
                    func.ST_Touches(District.geom, target),
                    func.ST_Length(func.ST_Transform(func.ST_Intersection(District.geom, target), 3750)) > 1,
                )
                .order_by(District.number)
            )
        )
    return ids


def observations(geo, codes):
    validate_geography(geo)
    definitions = catalog()
    if not codes or len(codes) > 12 or any(c not in definitions for c in codes):
        raise ValueError("Unknown or excessive indicator selection; search approved metadata first")
    mapped = {
        s["indicator"]: s
        for s in statistics(geo)
        if s["source"]["id"] == "acs-2024-5yr" and s["reference_period"] == PERIOD
    }
    with session() as db:
        original = {
            (r.profile, r.row_number): r
            for r in db.scalars(
                select(ACSProfileObservation).where(
                    ACSProfileObservation.geography_id == geo,
                    ACSProfileObservation.source_id == "acs-2024-5yr",
                    ACSProfileObservation.reference_period == PERIOD,
                )
            )
        }
        src = db.get(Source, "acs-2024-5yr")
        native = {
            r.indicator: (r, s)
            for r, s in db.execute(
                select(Statistic, Source)
                .join(Source)
                .where(
                    Statistic.geography_id == geo,
                    Statistic.reference_period == PERIOD,
                    Source.status == "approved",
                    Source.id.like("acs-2024-detailed-%"),
                )
            )
        }

        def read(code):
            spec = definitions[code]
            if code in mapped:
                return {**mapped[code], "universe": spec["universe"]}
            if code in RAW:
                r = original.get((spec["profile"], spec["row"]))
                if r is None:
                    raise ValueError("Reviewed profile row missing")
                measure = spec["measure"]
                moe_measure = "percent_moe" if measure == "percent" else "moe"
                p = {
                    **r.provenance,
                    "estimate_cell": r.provenance["cells"][measure],
                    "moe_cell": r.provenance["cells"][moe_measure],
                    "raw_estimate": r.raw_values[measure],
                    "raw_moe": r.raw_values[moe_measure],
                    "variable_definition": spec["label"],
                    "universe": spec["universe"],
                    "denominator": spec["denominator"],
                    "original_definition": r.definition,
                    "section": r.section,
                    "measure": measure,
                }
                return {
                    "id": f"research:{geo}:{code}",
                    "indicator": code,
                    "label": spec["label"],
                    "unit": spec["unit"],
                    "universe": spec["universe"],
                    "estimate": getattr(r, measure),
                    "moe": getattr(r, moe_measure),
                    "geographic_level": geo.split("-")[0],
                    "boundary_vintage": 2022 if geo.startswith(("house-", "senate-")) else None,
                    "reference_period": r.reference_period,
                    "method": "reported_profile",
                    "status": "available" if getattr(r, measure) is not None else "unavailable_or_suppressed",
                    "source": {"id": src.id, "title": src.title, "url": src.url},
                    "provenance": p,
                    "provenance_url": f"/v1/research/observations/{geo}/{code}/provenance",
                }
            if "operation" in spec:
                inputs = [read(c) for c in spec["inputs"]]
                values = [i["estimate"] for i in inputs]
                moes = [i["moe"] for i in inputs]
                estimate = moe = None
                if all(v is not None for v in values):
                    if spec["operation"] == "sum":
                        estimate = sum(values)
                        moe = (
                            math.sqrt(sum(m * m for m in moes)) if all(m is not None for m in moes) else None
                        )
                    else:
                        d = sum(values[1:])
                        md = (
                            math.sqrt(sum(m * m for m in moes[1:]))
                            if all(m is not None for m in moes[1:])
                            else None
                        )
                        estimate, moe = subset_percentage(values[0], d, moes[0], md)
                base = inputs[0]
                return {
                    **base,
                    "id": f"research:{geo}:{code}",
                    "indicator": code,
                    "label": spec["label"],
                    "unit": spec["unit"],
                    "universe": spec["universe"],
                    "estimate": estimate,
                    "moe": moe,
                    "method": "derived_" + spec["operation"],
                    "status": "available" if estimate is not None else "unavailable_inputs",
                    "provenance": {
                        "variable_definition": spec["label"],
                        "universe": spec["universe"],
                        "inputs": [
                            {
                                "id": x["id"],
                                "indicator": x["indicator"],
                                "estimate": x["estimate"],
                                "moe": x["moe"],
                                "provenance": x["provenance"],
                            }
                            for x in inputs
                        ],
                        "formula": spec["operation"],
                        "moe_method": "Approximate RSS for disjoint sums; ACS subset percentage approximation for rates; covariance unavailable.",
                    },
                    "provenance_url": f"/v1/research/observations/{geo}/{code}/provenance",
                }
            if code in native:
                r, s = native[code]
                return {
                    "id": r.id,
                    "indicator": r.indicator,
                    "label": spec["label"],
                    "unit": r.unit,
                    "universe": spec["universe"],
                    "estimate": r.estimate,
                    "moe": r.moe,
                    "geographic_level": r.geographic_level,
                    "boundary_vintage": r.boundary_vintage,
                    "reference_period": r.reference_period,
                    "method": r.method,
                    "status": r.status,
                    "source": {"id": s.id, "title": s.title, "url": s.url},
                    "provenance": r.provenance,
                }
            raise ValueError("Indicator not imported for geography")

        return [read(c) for c in dict.fromkeys(codes)]
