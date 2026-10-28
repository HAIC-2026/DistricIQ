"""Mappings for the supplied DP02–DP05 workbooks. Cell labels are validated before import.
No detailed-table variable identifier is inferred from a profile label.
"""

WORKBOOK_FILES = {
    "house": "acs2024_5yr_house_hi.xlsx",
    "senate": "acs2024_5yr_senate_hi.xlsx",
    "county": "acs2024_5yr_counties_hi.xlsx",
    "state": "acs2024_5yr_state_hi.xlsx",
}
PROFILE_INDICATORS = {}


def define(code, sheet, row, label, unit, *, column=0, group=None, display_label=None):
    PROFILE_INDICATORS[code] = {
        "sheet": sheet,
        "row": row,
        "expected_label": label,
        "column": column,
        "label": display_label or label,
        "unit": unit,
        "display_group": group,
    }


define("population", "DP05", 4, "Total population", "people")
define("median_age", "DP05", 21, "Median age (years)", "years")
define("age_under_18", "DP05", 22, "Under 18 years", "people")
define("age_65_plus", "DP05", 27, "65 years and over", "people")
define("older_adult_share", "DP05", 27, "65 years and over", "percent", column=2)
define("median_household_income", "DP03", 70, "Median household income (dollars)", "USD")
define("per_capita_income", "DP03", 96, "Per capita income (dollars)", "USD")
define(
    "poverty_rate",
    "DP03",
    138,
    "All people",
    "percent",
    column=2,
    display_label="All people whose income in the past 12 months is below the poverty level",
)
define(
    "poverty_population",
    "DP03",
    138,
    "All people",
    "people",
    display_label="People below poverty (count not published in supplied profile)",
)
define("households", "DP02", 4, "Total households", "households")
define("total_housing_units", "DP04", 4, "Total housing units", "housing units")
define("owner_occupied", "DP04", 54, "Owner-occupied", "households")
define("renter_occupied", "DP04", 55, "Renter-occupied", "households")
define(
    "median_gross_rent", "DP04", 152, "Median (dollars)", "USD", display_label="Median gross rent (dollars)"
)
AGE_LABELS = [
    "Under 5 years",
    "5 to 9 years",
    "10 to 14 years",
    "15 to 19 years",
    "20 to 24 years",
    "25 to 34 years",
    "35 to 44 years",
    "45 to 54 years",
    "55 to 59 years",
    "60 to 64 years",
    "65 to 74 years",
    "75 to 84 years",
    "85 years and over",
]
for index, label in enumerate(AGE_LABELS, 1):
    define(f"age_profile_{index:02}", "DP05", 7 + index, label, "people", group="age_distribution")
INCOME_LABELS = [
    "Less than $10,000",
    "$10,000 to $14,999",
    "$15,000 to $24,999",
    "$25,000 to $34,999",
    "$35,000 to $49,999",
    "$50,000 to $74,999",
    "$75,000 to $99,999",
    "$100,000 to $149,999",
    "$150,000 to $199,999",
    "$200,000 or more",
]
for index, label in enumerate(INCOME_LABELS, 1):
    define(f"income_profile_{index:02}", "DP03", 59 + index, label, "households", group="income_distribution")
for code, row, label, display in [
    (
        "rent_burden_denominator",
        155,
        "Occupied units paying rent (excluding units where GRAPI cannot be computed)",
        "Rent burden universe",
    ),
    ("rent_burden_30_34", 160, "30.0 to 34.9 percent", "Rent: 30–34.9% of household income"),
    ("rent_burden_35_plus", 161, "35.0 percent or more", "Rent: 35% or more of household income"),
    (
        "mortgage_burden_denominator",
        127,
        "Housing units with a mortgage (excluding units where SMOCAPI cannot be computed)",
        "Mortgage owner-cost universe",
    ),
    ("mortgage_burden_30_34", 131, "30.0 to 34.9 percent", "Mortgaged owner costs: 30–34.9%"),
    ("mortgage_burden_35_plus", 132, "35.0 percent or more", "Mortgaged owner costs: 35% or more"),
    ("unmortgaged_burden_30_34", 140, "30.0 to 34.9 percent", "Unmortgaged owner costs: 30–34.9%"),
    ("unmortgaged_burden_35_plus", 141, "35.0 percent or more", "Unmortgaged owner costs: 35% or more"),
]:
    define(code, "DP04", row, label, "households", display_label=display)
# The DP03 percentage table provides neither the population count nor its poverty universe.
PROFILE_INDICATORS["poverty_denominator"] = {
    "sheet": "DP03",
    "row": 138,
    "expected_label": "All people",
    "column": None,
    "label": "Population with poverty status determined (not published in supplied profile)",
    "unit": "people",
    "display_group": None,
}
