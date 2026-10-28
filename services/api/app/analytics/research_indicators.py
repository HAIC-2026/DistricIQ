"""Reviewed semantics for preserved 2024 profile rows; never infer a universe from a label.

Worksheet rows are not Census API variable codes. New native tables keep their own metadata.
"""

RAW = {}


def define(profile, row, label, unit, universe, *, percent=False, tags="", denominator=None):
    code = f"{profile.lower()}_r{row:03}_{'percent' if percent else 'estimate'}"
    RAW[code] = {
        "code": code,
        "label": label,
        "profile": profile,
        "row": row,
        "measure": "percent" if percent else "estimate",
        "unit": "percent" if percent else unit,
        "universe": universe,
        "denominator": denominator,
        "keywords": tags,
        "method": "reported",
        "reference_period": "2020–2024",
        "source_id": "acs-2024-5yr",
    }
    return code


def pair(profile, row, label, unit, universe, **kwargs):
    for percent in (False, True):
        define(profile, row, label, unit, universe, percent=percent, **kwargs)


HH = "Households (occupied housing units); not individual residents"
EDU = "Population 25 years and over"
DISABILITY = "Civilian noninstitutionalized population; excludes institutional residents"
POVERTY = "Population for whom poverty status is determined; not all residents"

for row, label in [
    (5, "Married-couple households"),
    (7, "Cohabiting-couple households"),
    (9, "Male householder, no spouse/partner"),
    (13, "Female householder, no spouse/partner"),
    (17, "Households with one or more people under 18"),
    (18, "Households with one or more people 65+"),
    (11, "Male householder living alone"),
    (15, "Female householder living alone"),
    (12, "Male householder 65+ living alone"),
    (16, "Female householder 65+ living alone"),
]:
    pair(
        "DP02",
        row,
        label,
        "households",
        HH,
        tags="family composition children older kupuna alone",
        denominator="DP02 row 4 total households",
    )

for row, label in [
    (51, "Grandparents living with own grandchildren under 18"),
    (52, "Grandparents responsible for grandchildren's basic needs"),
]:
    define(
        "DP02",
        row,
        label,
        "people",
        "Grandparents living with own grandchildren under 18",
        tags="grandparents caregivers raising grandchildren",
    )
for row, label in [
    (63, "Preschool enrollment"),
    (64, "Kindergarten enrollment"),
    (65, "Elementary enrollment grades 1–8"),
    (66, "High school enrollment grades 9–12"),
    (67, "College or graduate school enrollment"),
]:
    pair(
        "DP02",
        row,
        label,
        "people",
        "Population 3 years and over enrolled in school",
        tags="education school students",
        denominator="DP02 row 62",
    )
for row, label in [
    (70, "Less than ninth grade"),
    (71, "Ninth–twelfth grade, no diploma"),
    (72, "High school graduate or equivalency"),
    (73, "Some college, no degree"),
    (74, "Associate's degree"),
    (75, "Bachelor's degree"),
    (76, "Graduate or professional degree"),
    (77, "High school graduate or higher"),
    (78, "Bachelor's degree or higher"),
]:
    pair(
        "DP02",
        row,
        label,
        "people",
        EDU,
        tags="education educational attainment college degree bachelors",
        denominator="DP02 row 69",
    )
pair(
    "DP02",
    81,
    "Civilian veterans",
    "people",
    "Civilian population 18 years and over",
    tags="veterans",
    denominator="DP02 row 80",
)
for row, label, universe, denominator in [
    (84, "Residents with a disability", DISABILITY, "DP02 row 83"),
    (86, "Children under 18 with a disability", DISABILITY + "; under 18", "DP02 row 85"),
    (88, "Adults 18–64 with a disability", DISABILITY + "; age 18–64", "DP02 row 87"),
    (90, "Older adults 65+ with a disability", DISABILITY + "; age 65+", "DP02 row 89"),
]:
    pair(
        "DP02",
        row,
        label,
        "people",
        universe,
        tags="disability disabled health older kupuna",
        denominator=denominator,
    )
for row, label in [
    (173, "Households with a computer"),
    (174, "Households with a broadband internet subscription"),
]:
    pair(
        "DP02",
        row,
        label,
        "households",
        HH,
        tags="digital internet broadband computer access",
        denominator="DP02 computer/internet total households",
    )

for row, label in [
    (5, "People in the labor force"),
    (7, "Employed civilians"),
    (8, "Unemployed civilians"),
    (10, "People not in the labor force"),
]:
    define(
        "DP03",
        row,
        label,
        "people",
        "Population 16 years and over",
        tags="employment jobs labor unemployment",
    )
define(
    "DP03",
    12,
    "Unemployment rate",
    "percent",
    "Civilian labor force",
    percent=True,
    tags="unemployment jobless labor",
    denominator="DP03 row 11 civilian labor force",
)
for row, label in [
    (23, "Workers driving alone"),
    (24, "Workers carpooling"),
    (25, "Workers using public transportation"),
    (26, "Workers walking"),
    (27, "Workers using other transportation"),
    (28, "Workers working from home"),
]:
    pair(
        "DP03",
        row,
        label,
        "people",
        "Workers 16 years and over",
        tags="transportation commute access bus work remote",
        denominator="DP03 row 22",
    )
define(
    "DP03",
    29,
    "Mean travel time to work",
    "minutes",
    "Workers 16+ who did not work from home",
    tags="commute transportation travel time",
)
for row, label in [
    (74, "Households receiving Social Security income"),
    (76, "Households receiving retirement income"),
    (78, "Households receiving Supplemental Security Income (SSI)"),
    (80, "Households receiving cash public assistance income"),
    (82, "Households reporting SNAP food benefits in the past 12 months"),
]:
    pair(
        "DP03",
        row,
        label,
        "households",
        HH,
        tags="income sources receipt benefits social security retirement fixed income assistance snap food ssi",
        denominator="DP03 row 59",
    )
for row, label, universe in [
    (
        75,
        "Mean Social Security income among recipient households",
        "Households receiving Social Security income, all householder ages",
    ),
    (
        77,
        "Mean retirement income among recipient households",
        "Households receiving retirement income, all householder ages",
    ),
    (79, "Mean SSI income among recipient households", "Households receiving Supplemental Security Income"),
    (
        81,
        "Mean cash public assistance among recipient households",
        "Households receiving cash public assistance income",
    ),
    (94, "Median family income", "Families"),
]:
    define("DP03", row, label, "USD", universe, tags="income retirement social security benefits family")
for row, label, universe, denominator in [
    (105, "Residents with health insurance", DISABILITY, "DP03 row 104"),
    (106, "Residents with private health insurance", DISABILITY, "DP03 row 104"),
    (107, "Residents with public health coverage", DISABILITY, "DP03 row 104"),
    (108, "Residents without health insurance", DISABILITY, "DP03 row 104"),
    (110, "Children under 19 without health insurance", DISABILITY + "; under 19", "DP03 row 109"),
]:
    pair(
        "DP03",
        row,
        label,
        "people",
        universe,
        tags="health insurance coverage uninsured medicaid",
        denominator=denominator,
    )
for row, label, universe in [
    (129, "Families below poverty", "Families for whom poverty status is determined"),
    (139, "Children under 18 below poverty", POVERTY + "; under 18"),
    (145, "Older adults 65+ below poverty", POVERTY + "; age 65+"),
]:
    define(
        "DP03",
        row,
        label,
        "percent",
        universe,
        percent=True,
        tags="poverty income hardship children older kupuna",
    )
for row, label in [
    (68, "Households without a vehicle"),
    (69, "Households with one vehicle"),
    (70, "Households with two vehicles"),
    (71, "Households with three or more vehicles"),
    (91, "Occupied units with 1.01–1.50 occupants per room"),
    (92, "Occupied units with 1.51 or more occupants per room"),
]:
    pair(
        "DP04",
        row,
        label,
        "households",
        HH,
        tags="housing overcrowding crowding transportation vehicle car access",
        denominator="Occupied housing units",
    )
define(
    "DP04",
    134,
    "Owner cost-burden universe without mortgage",
    "households",
    "Owner-occupied units without a mortgage and with computable housing-cost share",
    tags="housing burden denominator",
)

DERIVED = {
    "older_adults_living_alone": {
        "label": "Adults 65+ living alone",
        "unit": "people",
        "universe": "People 65+ living in one-person households; excludes group quarters",
        "inputs": ["dp02_r012_estimate", "dp02_r016_estimate"],
        "operation": "sum",
        "keywords": "older kupuna seniors alone living arrangements",
    },
    "household_income_under_50000": {
        "label": "Households with annual income below $50,000 (2024 dollars)",
        "unit": "households",
        "universe": HH,
        "inputs": [f"income_profile_{i:02}" for i in range(1, 6)],
        "operation": "sum",
        "keywords": "households income less under 50000 hardship",
    },
    "housing_burden_30_plus": {
        "label": "Households spending 30% or more of income on housing",
        "unit": "households",
        "universe": "Occupied housing units with computable housing-cost shares; excludes not-computed cases",
        "inputs": [
            "rent_burden_30_34",
            "rent_burden_35_plus",
            "mortgage_burden_30_34",
            "mortgage_burden_35_plus",
            "unmortgaged_burden_30_34",
            "unmortgaged_burden_35_plus",
        ],
        "operation": "sum",
        "keywords": "housing burden affordability housing costs 30 percent",
    },
    "housing_burden_30_plus_share": {
        "label": "Share spending 30% or more on housing, among computable households",
        "unit": "percent",
        "universe": "Occupied units with computable housing-cost shares",
        "inputs": [
            "housing_burden_30_plus",
            "rent_burden_denominator",
            "mortgage_burden_denominator",
            "dp04_r134_estimate",
        ],
        "operation": "subset",
        "keywords": "housing burden share percent 30 affordability",
    },
    "owner_household_share": {
        "label": "Owner-occupied household share",
        "unit": "percent",
        "universe": HH,
        "inputs": ["owner_occupied", "households"],
        "operation": "subset",
        "keywords": "homeowners owners tenure ownership share",
    },
}
