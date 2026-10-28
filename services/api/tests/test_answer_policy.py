import pytest

from app.ai.answer_policy import (
    AnswerMismatch,
    check_selection,
    person_universe_mismatch,
    requirements,
    unsupported_intersection,
)


@pytest.mark.parametrize(
    "question,expected",
    [
        ("How many older people rely primarily on Social Security?", "joint"),
        ("Which families struggle to afford basic necessities?", "hardship"),
        ("How many households are at risk of housing instability?", "instability"),
        ("Is median rent higher than the rest of Honolulu County?", "remainder"),
        ("What population trends can guide services?", "trends"),
        ("How many households qualify for SNAP?", "eligibility"),
        ("Do older residents rent or own?", "householder"),
        ("What percentage of residents live in owner-occupied housing?", "householder"),
    ],
)
def test_unmeasured_conditions_are_explicit(question, expected):
    assert expected in requirements(question)["limitations"]


@pytest.mark.parametrize(
    "question,facts,calls",
    [
        ("What percentage are 65+?", [{"indicator": "age_65_plus", "unit": "people"}], []),
        (
            "How many renters are severely cost burdened?",
            [{"indicator": "rent_burden_35_plus", "unit": "households"}],
            [],
        ),
        (
            "Poverty rates in neighboring districts?",
            [{"indicator": "poverty_rate", "unit": "percent"}],
            ["compare_districts"],
        ),
        (
            "How many households earn less than $50,000?",
            [{"indicator": "income_profile_01", "unit": "households"}],
            [],
        ),
    ],
)
def test_related_data_cannot_substitute_for_requested_measure(question, facts, calls):
    with pytest.raises(AnswerMismatch):
        check_selection(requirements(question), facts, calls)


def test_compatible_native_severe_burden_and_approved_sum_are_allowed():
    check_selection(
        requirements("How many severely burdened renters?"),
        [{"indicator": "B25070_010", "unit": "households"}],
        [],
    )


def test_separate_marginals_do_not_prove_an_unpublished_joint_population():
    policy = requirements("How many people 65+ live alone, rent and receive Social Security?")
    separate = [
        {"label": "Householder 65+ living alone", "universe": "Households"},
        {"label": "Households receiving Social Security income", "universe": "Households all ages"},
        {"label": "Renter households", "universe": "Households"},
    ]
    assert unsupported_intersection(policy, separate)
    supported = requirements("How many older householders live alone and rent?")
    assert not unsupported_intersection(
        supported,
        [
            {
                "label": "Renter occupied / Householder living alone / Householder 65 years and over",
                "universe": "Occupied housing units",
            }
        ],
    )


def test_person_request_cannot_be_answered_as_household_receipt():
    policy = requirements("How many people live in households receiving SNAP?")
    assert person_universe_mismatch(policy, [{"unit": "households", "universe": "Households"}])
    assert not person_universe_mismatch(
        requirements("What percentage of households have children?"),
        [{"unit": "percent", "universe": "Households with children"}],
    )
    assert not person_universe_mismatch(
        policy, [{"unit": "people", "universe": "Population in SNAP households"}]
    )
    check_selection(
        requirements("How many households earn less than $50,000?"),
        [{"indicator": "household_income_under_50000", "unit": "households"}],
        [],
    )


def test_broad_older_tenure_and_income_context_use_complete_reviewed_measures():
    p = requirements("Are older residents more likely to rent or own?")
    with pytest.raises(AnswerMismatch, match="reviewed older_owner"):
        check_selection(p, [{"indicator": "B25011_007", "unit": "households"}], [])
    check_selection(p, [{"indicator": c, "unit": "households"} for c in
                        ("older_owner_households", "older_renter_households")], [])
    with pytest.raises(AnswerMismatch, match="too narrow"):
        check_selection(requirements("How many kupuna live on fixed incomes?"),
                        [{"indicator": "B17001_029", "unit": "people"}], [])
