"""Contracts for seven answer styles, using deliberately synthetic source fixtures."""

import pytest

from app.ai.answer_policy import requirements
from app.ai.district_assistant import render
from app.ai.district_tools import Evidence
from app.ai.response_presenter import md
from app.schemas.assistant import AnswerSelection


def fact(ref="s1", **changes):
    return {
        "ref": ref, "statistic_id": ref, "indicator": "population",
        "geography": "House District 30", "geography_id": "house-30",
        "label": "Total population", "estimate": 123, "moe": 7,
        "unit": "people", "reference_period": "2020–2024", "boundary_vintage": 2022,
        "geographic_level": "house", "universe": "Total population", "method": "reported",
        "source": {"id": "fixture", "title": "Synthetic ACS fixture", "url": "https://www.census.gov"},
        "provenance_url": "/v1/statistics/fixture/provenance", **changes,
    }


def response(facts=None, question="population", **selection):
    e = Evidence()
    e.districts.add("house-30")
    e.policy = requirements(question)
    e.facts = {f["ref"]: f for f in (facts if facts is not None else [fact()])}
    s = AnswerSelection(
        **{"intent": "facts", "fact_refs": list(e.facts), "comparison_refs": [],
           "active_district_id": "house-30", "explanations": [], **selection}
    )
    return render(s, e)


def test_exact_answer_leads_with_value_and_omits_unrequested_structure():
    r = response()
    assert r["message"].startswith("The estimate for **total population**")
    assert "**123 people** (±7). [s1]" in r["message"]
    assert r["message"].count("2020–2024") == 1
    assert "What this means" not in r["message"] and "next question" not in r["message"]
    assert r["citations"][0]["universe"] == "Total population"
    assert "Universe:" not in r["message"]


def test_related_context_is_readable_and_never_relabels_household_receipt():
    f = fact(label="Households with Social Security income", indicator="dp03_r074_estimate",
             estimate=12, unit="households", universe="Households, all ages")
    r = response([f], question="How many older people rely on fixed incomes?",
                 intent="context", insight="income_sources", presentation="key_findings")
    assert r["answerability"] == "partially_answerable"
    assert r["message"].startswith("An exact count")
    assert "- Households with Social Security income: **12 households**" in r["message"]
    assert "not individual older residents" in r["message"]
    assert "What this means" in r["message"]
    assert "12 people" not in r["message"]
    assert "exact requested measure is not established" not in r["message"]


def test_individual_request_gets_material_householder_limit_in_main_answer():
    r = response([fact(unit="households", label="Older renter households", universe="Households")],
                 question="How many older people rent their homes?")
    assert r["answerability"] == "partially_answerable"
    assert "not individual residents" in r["message"]
    assert "householder's age" in r["message"]


def test_comparison_table_uses_operands_units_citations_and_code_calculation():
    e = Evidence()
    e.districts.update(["house-30", "house-31"])
    e.facts = {"s1": fact(unit="percent", label="Poverty rate", estimate=10, moe=2),
               "s2": fact("s2", geography="House District 31", geography_id="house-31",
                          unit="percent", label="Poverty rate", estimate=7, moe=1)}
    e.delta(e.facts["s1"], e.facts["s2"])
    r = render(AnswerSelection(intent="comparison", fact_refs=["s1"], comparison_refs=["d1"],
                              active_district_id="house-30", explanations=[], presentation="table"), e)
    assert "| Measure | House District 30 | House District 31 |" in r["message"]
    assert "**10%** (±2 percentage points) [s1]" in r["message"]
    assert "3 percentage points" in r["message"]
    assert "does not test statistical significance" in r["message"]
    assert len(r["citations"]) == 2 and r["methodology"]
    assert "2020–2024" in r["message"]


def test_uncertainty_question_explains_confidence_without_unrequested_warning_dump():
    r = response([fact(unit="USD", label="Median household income", estimate=500, moe=20)],
                 intent="moe", question="Explain its margin of error")
    assert "**$500** (±$20)" in r["message"]
    assert "90% confidence level" in r["message"]
    assert "not zero" not in r["message"]


def test_programs_keep_reported_rules_dates_official_links_and_no_eligibility_claim():
    e = Evidence()
    e.calls = ["search_programs"]
    e.programs = [{"id": "fixture", "name": "Example assistance", "purpose_benefits": "Test benefit.",
                   "eligibility_url": "https://example.gov/eligibility", "verification_date": "2026-10-26",
                   "age_income_household_residency_disability_rules": "Reported age rule: 65+.",
                   "application_availability": "Waitlist closed."}]
    r = render(AnswerSelection(intent="programs", fact_refs=[], comparison_refs=[],
                              active_district_id=None, explanations=[]), e)
    assert "[Example assistance](https://example.gov/eligibility)" in r["message"]
    assert "65+" in r["message"] and "Waitlist closed" in r["message"]
    assert "2026-10-26" in r["message"] and "remain incomplete" in r["message"]
    assert r["answerability"] == "program_information"
    assert "You qualify" not in r["message"]


def test_unsupported_answer_drops_unrelated_numeric_evidence_and_offers_next_step():
    r = response(intent="unsupported", question="Exact primary-income dependence")
    assert r["answerability"] == "unsupported" and r["citations"] == []
    assert "123" not in r["message"] and "reliable count or percentage" in r["message"]
    assert "next step" in r["message"]


def test_relevance_order_and_interpretation_are_bounded_by_selected_evidence():
    f1, f2 = fact(), fact("s2", label="Median age", estimate=50, unit="years")
    r = response([f1, f2], intent="summary", fact_refs=["s2", "s1"], insight="income_sources")
    assert r["message"].index("Median age") < r["message"].index("Total population")
    assert "What this means" not in r["message"]  # Cannot attach an unrelated insight.
    assert [c["ref"] for c in r["citations"]] == ["s2", "s1"]
    r = response([f1, f2], fact_refs=["s2"])
    assert len(r["citations"]) == 1 and "123" not in r["message"]


def test_derived_and_unavailable_margins_remain_explicit_once():
    r = response([fact(method="derived_sum", moe=None), fact("s2", method="derived_sum")])
    assert "margin of error unavailable" in r["message"]
    assert r["message"].count("covariance") == 1
    assert "(calculated)" in r["message"]


def test_imported_labels_cannot_create_markdown_citations_or_table_cells():
    assert md("A | B [s99] **bad**") == r"A \| B \[s99\] \*\*bad\*\*"
    with pytest.raises(ValueError, match="not retrieved"):
        response(fact_refs=["s99"])


def test_only_retrieved_programs_can_be_prioritized_and_unrelated_caveats_are_omitted():
    e = Evidence()
    p = {"id": "a", "name": "Program A", "purpose_benefits": "Support.",
         "eligibility_url": "https://example.gov", "verification_date": "2026-10-26",
         "age_income_household_residency_disability_rules": "Rules need checking.",
         "application_availability": "Unknown."}
    e.programs = [p, {**p, "id": "b", "name": "Program B"}]
    s = AnswerSelection(intent="programs", fact_refs=[], comparison_refs=[],
                        active_district_id=None, explanations=[], program_ids=["b"])
    r = render(s, e)
    assert [p["id"] for p in r["programs"]] == ["b"]
    with pytest.raises(ValueError, match="retrieved programs"):
        render(s.model_copy(update={"program_ids": ["invented"]}), e)
    r = response([], intent="unsupported", explanations=["joint"],
                 question="How many residents were evicted last month?")
    assert "fixed income" not in r["message"]
    assert "eviction or homelessness" in r["message"]


def test_fixed_income_context_rejects_unfocused_evidence_and_excess_program_lists():
    from app.ai.answer_policy import AnswerMismatch

    facts = [fact(f"s{i}", label="Households with Social Security income", unit="households")
             for i in range(1, 5)]
    with pytest.raises(AnswerMismatch, match="at most three"):
        response(facts, question="How many older adults live on fixed incomes?", intent="context")
    with pytest.raises(AnswerMismatch, match="Tenure counts"):
        response([fact(label="Owner households with householder 65+", unit="households")],
                 question="How many older adults live on fixed incomes?", intent="context")


def test_tenure_interpretation_uses_compatible_retrieved_household_estimates_only():
    from app.ai.response_presenter import tenure_finding

    pair = [fact(indicator="older_owner_households", estimate=50, unit="households"),
            fact("s2", indicator="older_renter_households", estimate=60, unit="households")]
    assert "**renter-occupied household** estimate is higher" in tenure_finding(pair)
    assert "[s1] [s2]" in tenure_finding(pair)
    assert "significance test" in tenure_finding(pair)
    assert tenure_finding([pair[0], {**pair[1], "geography_id": "house-31"}]) is None
    assert tenure_finding([pair[0], {**pair[1], "reference_period": "2015–2019"}]) is None
    r = response(intent="facts", explanations=["comparison"])
    assert "Differences are calculated" not in r["message"]


def test_income_receipt_explanation_does_not_repeat_unrelated_tenure_caveat():
    f = fact(label="Households with Social Security income", unit="households")
    r = response([f], question="How many older people live on fixed incomes?",
                 intent="context", insight="income_sources", explanations=["householder", "joint"])
    assert "not individual older residents" in r["message"]
    assert "Tenure by age" not in r["message"]
    assert r["message"].count("Household totals") == 1
