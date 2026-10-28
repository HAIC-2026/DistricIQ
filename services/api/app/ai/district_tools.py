"""Allowlisted read-only operations. Models never receive SQL, file or mutation tools."""

import re
from typing import Annotated, Literal

from pydantic import AfterValidator, Field, StringConstraints

from app.analytics.acs_profiles import PROFILE_INDICATORS
from app.analytics.research_indicators import DERIVED, RAW
from app.schemas.assistant import AnswerSelection, DistrictId
from app.schemas.discovery import StrictModel
from app.services import research_service
from app.services.comparison_service import compare_county, compare_state
from app.services.district_service import get_district, statistics
from app.services.program_service import get_program, search_programs


def approved_identifier(code):
    if (
        code not in PROFILE_INDICATORS
        and code not in RAW
        and code not in DERIVED
        and code
        not in {
            "older_poverty_count",
            "child_poverty_count",
            "older_owner_households",
            "older_renter_households",
            "older_household_income_under_50000",
        }
        and not re.fullmatch(r"B(?:17001|25070|25007|25011|19037)_\d{3}", code)
    ):
        raise ValueError("Search approved indicator metadata first")
    return code


Indicator = Annotated[
    str, StringConstraints(min_length=1, max_length=80), AfterValidator(approved_identifier)
]
SUMMARY = [
    "population",
    "median_household_income",
    "poverty_rate",
    "median_age",
    "older_adult_share",
    "median_gross_rent",
]


class DistrictInput(StrictModel):
    district_id: DistrictId


class IndicatorsInput(DistrictInput):
    indicators: list[Indicator] = Field(min_length=1, max_length=8)


class DistrictComparison(StrictModel):
    left_id: DistrictId
    right_id: DistrictId
    indicators: list[Indicator] = Field(min_length=1, max_length=6)


class BenchmarkInput(IndicatorsInput):
    benchmark: Literal["county", "state"]


class DistributionInput(DistrictInput):
    distribution: Literal["age", "income"]
    order: Literal["published", "largest"]


class SearchInput(StrictModel):
    query: str = Field(min_length=2, max_length=300)


class ProgramInput(StrictModel):
    program_id: str = Field(min_length=2, max_length=80)


class ResearchInput(DistrictInput):
    indicators: list[str] = Field(min_length=1, max_length=12)


class ResearchComparison(StrictModel):
    left_id: DistrictId
    right_id: DistrictId | None
    benchmark: Literal["county", "state"] | None
    indicators: list[str] = Field(min_length=1, max_length=6)


TOOLS = {
    "compare_neighbors": (
        ResearchInput,
        "Compare approved indicator IDs with all same-chamber districts sharing a land boundary longer than one metre, using existing PostGIS polygons. Point-only contacts and across-water proximity are excluded. Never assume consecutive district numbers are neighbors.",
    ),
    "search_programs": (
        SearchInput,
        "Find official government programs by population/need/purpose. Source dates, application/waitlist status and unresolved rules are retained. Discovery and potential relevance only, never individual eligibility from ACS statistics.",
    ),
    "get_program": (
        ProgramInput,
        "Read one program ID returned by search_programs, with official documentation, application route, service area, verification dates and incomplete criteria.",
    ),
    "search_indicators": (
        SearchInput,
        "Search approved statistical metadata by meaning, topic and subgroup. Returns IDs, units, universes, recipes and availability. Use before retrieving education, disability, benefit receipt, older-alone, housing burden or other unmapped fields. Never infer an intersection from separate matches.",
    ),
    "get_observations": (
        ResearchInput,
        "Read approved IDs returned by search_indicators from original profile rows or imported detailed tables, including MOEs, universes and original sources. Reviewed derived recipes are calculated by the server.",
    ),
    "compare_observations": (
        ResearchComparison,
        "Compare approved indicator IDs for two districts (right_id, benchmark=null), or with county/state (right_id=null, benchmark). Definitions, universes and periods must match. No arbitrary county substitution.",
    ),
    "get_district_profile": (DistrictInput, "Read the district's six summary indicators from PostgreSQL."),
    "get_district_indicators": (IndicatorsInput, "Read specific available indicators, estimates and MOEs."),
    "compare_districts": (
        DistrictComparison,
        "Compare two named legislative districts using compatible ACS indicators. Left minus right is calculated in code.",
    ),
    "compare_benchmark": (
        BenchmarkInput,
        "Compare with the corresponding county context or Hawaiʻi state. Preserve the county comparison rule.",
    ),
    "get_distribution": (
        DistributionInput,
        "Read all original age or income brackets. Use largest order for biggest groups; brackets have unequal widths.",
    ),
    "get_housing_statistics": (
        DistrictInput,
        "Read the district's housing, tenure, rent and cost burden indicators.",
    ),
    "get_statistic_sources": (
        IndicatorsInput,
        "Read original ACS workbook cells, reported estimates and source metadata for these indicators.",
    ),
    "explain_available_indicators": (
        DistrictInput,
        "List supported indicators and retrieve unavailable mapped fields; explain limits, without inventing new variables.",
    ),
    "present_answer": (
        AnswerSelection,
        "Finish with only the most relevant retrieved fact/comparison references, in priority order. Choose presentation, optional evidence-supported insight and useful follow_up, or null. The server composes readable prose, values and citations. Use clarification or out_of_scope with empty refs when appropriate.",
    ),
}


def definitions():
    def strict_schema(schema):
        result = schema.model_json_schema()
        # Nullable presentation choices remain optional in our Python contract, but
        # OpenAI strict function schemas require every property, including nulls.
        result["required"] = list(result["properties"])
        for prop in result["properties"].values():
            prop.pop("default", None)
        return result

    return [
        {
            "type": "function",
            "name": name,
            "description": description,
            "strict": True,
            "parameters": strict_schema(schema),
        }
        for name, (schema, description) in TOOLS.items()
    ]


class Evidence:
    def __init__(self):
        self.facts = {}
        self.comparisons = {}
        self.districts = set()
        self.warnings = []
        self.calls = []
        self.programs = []
        self.policy = {}

    def context(self, district_id):
        get_district(district_id)
        self.districts.add(district_id)

    def selected_rows(self, geo, codes):
        if codes and any(c not in PROFILE_INDICATORS for c in codes):
            return research_service.observations(geo, codes)
        return [r for r in self.rows(geo) if codes is None or r["indicator"] in codes]

    def rows(self, geo):
        # Keep optional source imports out of this assistant's statistical scope.
        specs = research_service.catalog(native=False)
        return [
            {**s, "universe": specs.get(s["indicator"], {}).get("universe", s.get("universe"))}
            for s in statistics(geo)
            if s["source"]["id"] == "acs-2024-5yr" and s["reference_period"] == "2020–2024"
        ]

    def add(self, geo, name, rows):
        output = []
        for s in rows:
            existing = next((f for f in self.facts.values() if f["statistic_id"] == s["id"]), None)
            if existing:
                output.append(existing)
                continue
            p = s["provenance"]
            fact = {
                "ref": f"s{len(self.facts) + 1}",
                "statistic_id": s["id"],
                "geography_id": geo,
                "geography": name,
                "indicator": s["indicator"],
                "label": s["label"],
                "estimate": s["estimate"],
                "moe": s["moe"],
                "unit": s["unit"],
                "reference_period": s["reference_period"],
                "status": s["status"],
                "geographic_level": s["geographic_level"],
                "boundary_vintage": s["boundary_vintage"],
                "source": s["source"],
                "provenance_url": f"/v1/statistics/{s['id']}/provenance",
                "workbook_url": p.get("workbook_url"),
                "workbook": p.get("workbook"),
                "sheet": p.get("sheet"),
                "estimate_cell": p.get("estimate_cell"),
                "moe_cell": p.get("moe_cell"),
                "raw_estimate": p.get("raw_estimate"),
                "raw_moe": p.get("raw_moe"),
                "workbook_sha256": p.get("workbook_sha256"),
                "universe": s.get("universe", p.get("universe")),
                "method": s.get("method", "reported"),
                "variables": s.get("variables", p.get("variables", [])),
            }
            fact["provenance_url"] = s.get("provenance_url", fact["provenance_url"])
            self.facts[fact["ref"]] = fact
            output.append(fact)
        return output

    def district(self, district_id, codes=None):
        district = get_district(district_id)
        self.districts.add(district_id)
        rows = self.selected_rows(district_id, codes)
        return district, rows

    def delta(self, left, right):
        if left.get("universe") and right.get("universe") and left["universe"] != right["universe"]:
            raise ValueError("Incompatible statistical universes")
        if (left["indicator"], left["unit"], left["reference_period"], left["boundary_vintage"]) != (
            right["indicator"],
            right["unit"],
            right["reference_period"],
            right["boundary_vintage"],
        ):
            # County/state records correctly have no legislative boundary vintage.
            if not (
                right["geographic_level"] in ("county", "state")
                and (left["indicator"], left["unit"], left["reference_period"])
                == (right["indicator"], right["unit"], right["reference_period"])
            ):
                raise ValueError("Incompatible definitions, units, periods or boundary plans")
        if left["estimate"] is None or right["estimate"] is None:
            return
        ref = f"d{len(self.comparisons) + 1}"
        self.comparisons[ref] = {
            "ref": ref,
            "left_ref": left["ref"],
            "right_ref": right["ref"],
            "difference": round(left["estimate"] - right["estimate"], 6),
            "unit": "percentage points" if left["unit"] == "percent" else left["unit"],
            "method": "Calculated left estimate minus right estimate; not a reported ACS estimate. No difference MOE or significance test calculated.",
        }

    def dispatch(self, name, arguments):
        if name not in TOOLS or name == "present_answer":
            raise ValueError("Unregistered data tool")
        value = TOOLS[name][0].model_validate_json(arguments)
        self.calls.append(name)
        if name in ("search_programs", "get_program"):
            self.programs = (
                search_programs(value.query) if name == "search_programs" else [get_program(value.program_id)]
            )
            return {"programs": self.programs, "individual_eligibility_supported": False}
        if name == "search_indicators":
            return {
                "indicators": research_service.search(value.query),
                "limitation": "Matches are separate measures unless an explicitly supported joint table or reviewed recipe is identified. Receipt is not dependence or eligibility.",
            }
        if name in ("get_observations", "compare_observations", "compare_neighbors"):
            left_id = (
                value.district_id if name in ("get_observations", "compare_neighbors") else value.left_id
            )
            ld = get_district(left_id)
            self.districts.add(left_id)
            left = self.add(left_id, ld["name"], research_service.observations(left_id, value.indicators))
            if name == "compare_neighbors":
                if len(value.indicators) > 3:
                    raise ValueError("Neighbor comparisons allow at most three indicators")
                for neighbor in research_service.neighbors(left_id):
                    rd = get_district(neighbor)
                    right = self.add(
                        neighbor, rd["name"], research_service.observations(neighbor, value.indicators)
                    )
                    for a in left:
                        for b in right:
                            if a["indicator"] == b["indicator"]:
                                self.delta(a, b)
                self.warnings.append(
                    "Neighbors are same-chamber 2022 districts with a shared land boundary longer than one metre (rook adjacency). Point contacts and nearby districts across water are excluded. Differences are descriptive, not significance tests."
                )
            elif name == "compare_observations":
                if bool(value.right_id) == bool(value.benchmark):
                    raise ValueError("Specify exactly one right district or benchmark")
                if value.right_id:
                    rd = get_district(value.right_id)
                    self.districts.add(value.right_id)
                    targets = [{"geography_id": rd["id"], "name": rd["name"]}]
                else:
                    result = (compare_county if value.benchmark == "county" else compare_state)(left_id)
                    targets = result["benchmarks"]
                    self.warnings.extend([result["caution"], result.get("comparison_rule", "")])
                for target in targets:
                    right = self.add(
                        target["geography_id"],
                        target["name"],
                        research_service.observations(target["geography_id"], value.indicators),
                    )
                    for a in left:
                        for b in right:
                            if a["indicator"] == b["indicator"]:
                                self.delta(a, b)
            return {
                "facts": list(self.facts.values()),
                "comparisons": list(self.comparisons.values()),
                "limitations": self.warnings,
            }
        codes = list(value.indicators) if hasattr(value, "indicators") else None
        if name == "compare_districts":
            ld, lr = self.district(value.left_id, codes)
            rd, rr = self.district(value.right_id, codes)
            left = self.add(ld["id"], ld["name"], lr)
            right = self.add(rd["id"], rd["name"], rr)
            for a in left:
                for b in right:
                    if a["indicator"] == b["indicator"]:
                        self.delta(a, b)
            self.warnings.append(
                "Comparisons are descriptive. Overlapping ACS estimates may not be independent; no statistical significance is asserted."
            )
        elif name == "compare_benchmark":
            result = (compare_county if value.benchmark == "county" else compare_state)(value.district_id)
            self.districts.add(value.district_id)
            left = self.add(
                value.district_id,
                result["district"]["name"],
                self.selected_rows(value.district_id, codes),
            )
            for b in result["benchmarks"]:
                right = self.add(
                    b["geography_id"],
                    b["name"],
                    self.selected_rows(b["geography_id"], codes),
                )
                for a in left:
                    for c in right:
                        if a["indicator"] == c["indicator"]:
                            self.delta(a, c)
            self.warnings.extend(
                [result["caution"], *([result["comparison_rule"]] if "comparison_rule" in result else [])]
            )
        else:
            district, rows = self.district(value.district_id, codes)
            if name == "get_district_profile":
                rows = [r for r in rows if r["indicator"] in SUMMARY]
            elif name == "get_distribution":
                rows = [r for r in rows if r["display_group"] == value.distribution + "_distribution"]
                rows.sort(
                    key=(lambda r: (r["estimate"] is None, -(r["estimate"] or 0)))
                    if value.order == "largest"
                    else (lambda r: r["display_order"])
                )
                self.warnings.append(
                    "Published age/income brackets have unequal widths; bracket counts are not comparable per-year rates."
                )
            elif name == "get_housing_statistics":
                rows = [
                    r
                    for r in rows
                    if PROFILE_INDICATORS.get(r["indicator"], {}).get("sheet") == "DP04"
                    or r["indicator"] == "households"
                ]
                if "B25070_010" in research_service.catalog():
                    rows.extend(research_service.observations(value.district_id, ["B25070_010"]))
            elif name == "explain_available_indicators":
                rows = [r for r in rows if r["estimate"] is None]
            self.add(district["id"], district["name"], rows)
        # Return complete bounded JSON; never slice JSON or silently omit source rows.
        result = {
            "facts": list(self.facts.values()),
            "comparisons": list(self.comparisons.values()),
            "limitations": list(dict.fromkeys(self.warnings)),
        }
        if name == "explain_available_indicators":
            result["discovery_note"] = (
                "These null aliases describe the original workbook fields. Search approved metadata for additional profile observations and imported detailed-table counts; a missing dashboard alias does not imply all data are unavailable."
            )
            result["supported_indicators"] = [
                {"code": k, "definition": v["label"], "unit": v["unit"]}
                for k, v in PROFILE_INDICATORS.items()
            ]
        return result
