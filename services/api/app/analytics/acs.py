"""Deterministic ACS detailed-table mappings. MOEs are 90% ACS margins, not standard errors."""

import math

INDICATORS = {
    "population": {
        "label": "Total population",
        "variables": ["B01003_001"],
        "unit": "people",
        "kind": "count",
    },
    "median_age": {"label": "Median age", "variables": ["B01002_001"], "unit": "years", "kind": "median"},
    "median_household_income": {
        "label": "Median household income",
        "variables": ["B19013_001"],
        "unit": "USD",
        "kind": "median",
    },
    "per_capita_income": {
        "label": "Per capita income",
        "variables": ["B19301_001"],
        "unit": "USD",
        "kind": "mean",
    },
    "poverty_population": {
        "label": "Population below poverty",
        "variables": ["B17001_002"],
        "unit": "people",
        "kind": "count",
    },
    "poverty_denominator": {
        "label": "Population with poverty status determined",
        "variables": ["B17001_001"],
        "unit": "people",
        "kind": "count",
    },
    "households": {
        "label": "Occupied households",
        "variables": ["B25003_001"],
        "unit": "households",
        "kind": "count",
    },
    "owner_occupied": {
        "label": "Owner occupied",
        "variables": ["B25003_002"],
        "unit": "households",
        "kind": "count",
    },
    "renter_occupied": {
        "label": "Renter occupied",
        "variables": ["B25003_003"],
        "unit": "households",
        "kind": "count",
    },
    "median_gross_rent": {
        "label": "Median gross rent",
        "variables": ["B25064_001"],
        "unit": "USD",
        "kind": "median",
    },
}
AGE_GROUPS = {
    "age_under_18": [*range(3, 7), *range(27, 31)],
    "age_18_34": [*range(7, 13), *range(31, 37)],
    "age_35_64": [*range(13, 20), *range(37, 44)],
    "age_65_plus": [*range(20, 26), *range(44, 50)],
}
for code, values in AGE_GROUPS.items():
    INDICATORS[code] = {
        "label": code.replace("age_", "Age ").replace("_", " "),
        "variables": [f"B01001_{v:03}" for v in values],
        "unit": "people",
        "kind": "count",
    }
for index, label in enumerate(
    [
        "Under $10k",
        "$10–15k",
        "$15–20k",
        "$20–25k",
        "$25–30k",
        "$30–35k",
        "$35–40k",
        "$40–45k",
        "$45–50k",
        "$50–60k",
        "$60–75k",
        "$75–100k",
        "$100–125k",
        "$125–150k",
        "$150–200k",
        "$200k+",
    ],
    2,
):
    INDICATORS[f"income_{index:02}"] = {
        "label": label,
        "variables": [f"B19001_{index:03}"],
        "unit": "households",
        "kind": "count",
    }
INDICATORS["poverty_rate"] = {
    "label": "Poverty rate",
    "variables": ["B17001_002", "B17001_001"],
    "unit": "percent",
    "kind": "rate",
}
INDICATORS["older_adult_share"] = {
    "label": "Residents aged 65+",
    "variables": INDICATORS["age_65_plus"]["variables"] + ["B01001_001"],
    "unit": "percent",
    "kind": "rate",
}


def numeric(value) -> float | None:
    try:
        x = float(value)
        return x if math.isfinite(x) and x >= 0 else None
    except (TypeError, ValueError):
        return None


def aggregate(row: dict, variables: list[str]) -> tuple[float | None, float | None]:
    estimates = [numeric(row.get(v + "E")) for v in variables]
    moes = [numeric(row.get(v + "M")) for v in variables]
    estimate = sum(estimates) if all(x is not None for x in estimates) else None
    moe = math.sqrt(sum(x * x for x in moes)) if all(x is not None for x in moes) else None
    return estimate, moe


def subset_percentage(n: float | None, d: float | None, mn: float | None, md: float | None):
    if n is None or d is None or d <= 0 or n > d:
        return None, None
    ratio = n / d
    moe = None
    if mn is not None and md is not None:
        term = mn**2 - ratio**2 * md**2
        # ACS subset formula; use the general ratio approximation if the radicand is negative.
        term = term if term >= 0 else mn**2 + ratio**2 * md**2
        moe = 100 * math.sqrt(term) / d
    return 100 * ratio, moe


def calculate(row: dict, code: str) -> dict:
    spec = INDICATORS[code]
    variables = spec["variables"]
    if spec["kind"] == "rate":
        n, mn = aggregate(row, variables[:-1])
        d, md = aggregate(row, variables[-1:])
        estimate, moe = subset_percentage(n, d, mn, md)
        method = "derived_subset_percentage"
    else:
        estimate, moe = aggregate(row, variables)
        method = "direct" if len(variables) == 1 else "derived_sum"
    return {
        "estimate": estimate,
        "moe": moe,
        "unit": spec["unit"],
        "variables": variables,
        "method": method,
        "status": "available" if estimate is not None else "unavailable_or_suppressed",
        "raw_values": {v + suffix: row.get(v + suffix) for v in variables for suffix in ("E", "M")},
    }
