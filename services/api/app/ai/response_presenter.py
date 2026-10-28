"""Readable answers composed exclusively from verified selections and source records.

The model chooses relevant evidence, layout and optional interpretation categories.
It cannot supply statistics, arithmetic, citations or unconstrained factual prose.
"""

import re
from urllib.parse import urlsplit

EXPLANATIONS = {
    "moe": "A margin of error describes sampling uncertainty at the 90% confidence level. For a percentage, the margin is in percentage points. It does not describe an individual resident or, by itself, establish a meaningful difference between districts.",
    "missing": "Unavailable or suppressed values are not zero. Some profile fields lack counts or denominators; separately imported detailed tables may provide them with their own definitions. Not every combined subgroup is available.",
    "comparison": "Differences are calculated from the reported estimates. They are descriptive; this comparison does not test statistical significance.",
    "housing": "Housing costs and cost burden help describe affordability pressures. They do not identify which households will lose housing or qualify for assistance. Medians describe the middle of a distribution, not an average household budget.",
    "bins": "These published age or income brackets have different widths. A larger group does not necessarily mean more people per year of age or households per dollar of income.",
    "joint": "Separate figures do not tell us how many people meet all the requested conditions. Adding or multiplying these groups would not give a reliable combined count.",
    "eligibility": "District demographics can help identify relevant programs, but cannot establish individual eligibility. The agency must check current household, income, resource, residency and any age or disability requirements, as well as availability.",
    "hardship": "Poverty, low income and housing cost burden describe different aspects of financial pressure. They are not an exact count of families unable to afford necessities, and families are not the same as households.",
    "instability": "Cost burden and crowding can help examine housing pressures. They do not predict eviction or homelessness, and overlapping groups cannot be added into one count of households at risk.",
    "remainder": "This benchmark covers the whole county, including the district. A median for the rest of the county cannot be found by subtracting the district's median.",
    "trends": "These figures describe one five-year period, rather than an annual trend. To assess change, we would need earlier estimates with compatible definitions and district boundaries.",
    "householder": "These figures count households, families or housing units, not individual residents. Tenure by age refers to the householder's age, not the age of everyone living there.",
}

# Short presentation labels for existing definitions; original labels and full
# universes remain attached to every citation and provenance response.
DISPLAY_LABELS = {
    "poverty_rate": "Poverty rate",
    "median_household_income": "Median household income",
    "median_gross_rent": "Median gross rent",
    "median_age": "Median age",
    "older_adult_share": "Residents age 65 and older",
    "age_under_18": "Residents under age 18",
    "age_65_plus": "Residents age 65 and older",
    "B25070_010": "Renter-occupied units spending 50% or more of household income on gross rent",
}


def label(fact):
    return md(DISPLAY_LABELS.get(fact["indicator"], fact["label"]))


def number(value, unit):
    if value is None:
        return "Unavailable"
    text = f"{value:,.1f}".removesuffix(".0")
    if unit == "USD":
        return "-$" + text[1:] if text.startswith("-") else "$" + text
    return text + ("%" if unit == "percent" else " " + unit)


def md(value):
    """Keep imported labels literal inside the limited Markdown presentation."""
    return re.sub(r"([\\`*_{}\[\]<>|])", r"\\\1", str(value)).replace("\n", " ")


def value_text(fact):
    text = number(fact["estimate"], fact["unit"])
    if fact["estimate"] is None:
        return "**Unavailable**"
    text = "**" + text + "**"
    if fact["moe"] is not None:
        # The estimate already gives the unit. Percentage MOEs need the explicit
        # percentage-point label so that ±2.6 is never interpreted as a percent change.
        margin = number(fact["moe"], "percentage points") if fact["unit"] == "percent" else number(
            fact["moe"], "USD" if fact["unit"] == "USD" else ""
        ).strip()
        text += " (±" + margin + ")"
    else:
        text += " (margin of error unavailable)"
    if fact.get("method", "").startswith("derived_"):
        text += " (calculated)"
    return text


def cite(fact):
    # Reference IDs originate with Evidence.add, never the model or a source URL.
    return "[" + fact["ref"] + "]"


def fact_line(fact, include_geography=False):
    text = label(fact)
    if include_geography:
        text += " — " + md(fact["geography"])
    return f"{text}: {value_text(fact)}. {cite(fact)}"


def safe_url(value):
    try:
        parsed = urlsplit(value)
        if parsed.scheme == "https" and parsed.hostname and not (parsed.username or parsed.password):
            return value.replace("(", "%28").replace(")", "%29").replace(" ", "%20")
    except ValueError:
        pass
    return None


def tenure_finding(facts):
    """Interpret a reviewed, mutually exclusive pair without inventing a rate."""
    owners = [f for f in facts if f["indicator"] == "older_owner_households"]
    renters = [f for f in facts if f["indicator"] == "older_renter_households"]
    if len(owners) != 1 or len(renters) != 1:
        return None
    owner, renter = owners[0], renters[0]
    if any(owner.get(k) != renter.get(k) for k in ("geography_id", "reference_period", "unit")):
        return None
    if any(f["estimate"] is None or f["unit"] != "households" for f in (owner, renter)):
        return None
    if owner["estimate"] == renter["estimate"]:
        finding = "the owner-occupied and renter-occupied estimates are equal at the reported precision"
    else:
        higher = "owner-occupied" if owner["estimate"] > renter["estimate"] else "renter-occupied"
        finding = f"the reported **{higher} household** estimate is higher"
    return (
        "Among households with a householder age 65 or older, " + finding
        + f". This is a descriptive comparison, without a statistical significance test. {cite(owner)} {cite(renter)}"
    )


def program_text(program):
    title = md(program["name"])
    url = safe_url(program["eligibility_url"])
    if url:
        title = f"[{title}]({url})"
    return (
        f"- **{title}** — {md(program['purpose_benefits'])} "
        f"{md(program['age_income_household_residency_disability_rules'])} "
        f"Application status: {md(program['application_availability'])}"
    )


def context_lead(explanations, geography, policy):
    place = f" in **{md(geography)}**" if geography else ""
    if "joint" in explanations and policy.get("income_dependence"):
        return (
            f"An exact count of residents who depend primarily on fixed or benefit income{place} "
            "isn't available in the current data. These related indicators can help describe the financial context."
        )
    leads = {
        "householder": "The available data describe households rather than individual residents. Here's the closest household-based evidence",
        "hardship": "The current data don't give an exact count of families unable to afford basic necessities. These indicators describe related financial pressures",
        "instability": "The current data don't identify an exact number of households facing housing instability. These indicators offer related context",
        "eligibility": "The current data can't tell us how many residents qualify for assistance. These indicators can help examine potential need",
        "remainder": "I can compare the district with the whole county, but not with the county excluding this district",
        "trends": "The current data support a demographic snapshot, rather than a trend over time",
        "joint": "An exact count of people meeting all those conditions isn't available. These related indicators offer context",
    }
    key = next((k for k in leads if k in explanations), "joint")
    return leads[key] + place + "."


def comparison_table(differences, evidence):
    # Long-form rows handle two districts, several benchmarks, or multiple measures
    # without implying that incompatible indicators share a statistical universe.
    pairs = {(d["left_ref"], d["right_ref"]) for d in differences}
    geographies = {(evidence.facts[a]["geography"], evidence.facts[b]["geography"]) for a, b in pairs}
    if len(geographies) == 1:
        left_name, right_name = next(iter(geographies))
        lines = [
            f"| Measure | {md(left_name)} | {md(right_name)} | Difference (first − second) |",
            "| --- | --- | --- | --- |",
        ]
        for d in differences:
            left, right = (evidence.facts[d[k]] for k in ("left_ref", "right_ref"))
            lines.append(
                f"| {label(left)} | {value_text(left)} {cite(left)} | "
                f"{value_text(right)} {cite(right)} | {number(d['difference'], d['unit'])} |"
            )
    else:
        lines = [
            "| Measure | First geography / estimate | Second geography / estimate | Difference (first − second) |",
            "| --- | --- | --- | --- |",
        ]
        for d in differences:
            left, right = (evidence.facts[d[k]] for k in ("left_ref", "right_ref"))
            lines.append(
                f"| {label(left)} | {md(left['geography'])}: {value_text(left)} {cite(left)} | "
                f"{md(right['geography'])}: {value_text(right)} {cite(right)} | {number(d['difference'], d['unit'])} |"
            )
    return "\n".join(lines)


def compose(selection, intent, facts, differences, explanations, programs, warnings, evidence):
    """Return readable Markdown plus full technical detail for an expandable panel."""
    lines, methodology = [], []
    geographies = list(dict.fromkeys(f["geography"] for f in facts))
    geography = geographies[0] if len(geographies) == 1 else None
    if intent == "context":
        lines.append(context_lead(explanations, geography, evidence.policy))
    elif intent == "summary":
        lines.append(f"Here's a snapshot of **{md(geography)}**." if geography else "Here are the key demographic findings.")
    elif intent == "programs":
        lines.append("These official programs may be relevant. The directory can guide further research; it doesn't determine whether someone qualifies.")
    elif intent == "unsupported":
        lines.append("That specific statistic isn't available in the current verified data, so I can't give a reliable count or percentage. Answering it would require a source that measures that outcome for the requested district and time period.")
    elif intent == "clarification":
        lines.append("Which House district (1–51) or Senate district (1–25) would you like to explore, and what would you like to know?")
    elif intent == "out_of_scope":
        lines.append("I can help research Hawaiʻi district demographics, housing, income, education, disability, public programs and comparisons. What district or community need would you like to explore?")
    elif intent == "missing":
        lines.append("These estimates aren't available in the current profile. An unavailable value means the figure wasn't reported here, rather than zero.")

    operands = {d[k] for d in differences for k in ("left_ref", "right_ref")}
    if differences:
        if len(differences) == 1:
            d = differences[0]
            left, right = (evidence.facts[d[k]] for k in ("left_ref", "right_ref"))
            if d["difference"]:
                higher = left if d["difference"] > 0 else right
                lines.append(f"The reported **{label(left).lower()}** estimate is higher in **{md(higher['geography'])}**. {cite(left)} {cite(right)}")
            else:
                lines.append(f"The reported **{label(left).lower()}** estimates are equal at the published precision. {cite(left)} {cite(right)}")
        if selection.presentation != "brief" or len(differences) > 1:
            lines.append(comparison_table(differences, evidence))
        else:
            d = differences[0]
            left, right = (evidence.facts[d[k]] for k in ("left_ref", "right_ref"))
            lines.append("\n".join("- " + fact_line(f, True) for f in (left, right)))
            lines.append(f"Calculated difference, first minus second: **{number(d['difference'], d['unit'])}**. {cite(left)} {cite(right)}")
    other = [f for f in facts if f["ref"] not in operands]
    if len(other) == 1 and intent in ("facts", "moe") and not differences:
        f = other[0]
        if f["estimate"] is None:
            lines.append(f"A reported estimate for **{label(f).lower()}** in **{md(f['geography'])}** isn't available. {cite(f)}")
        else:
            lines.append(f"The estimate for **{label(f).lower()}** in **{md(f['geography'])}** is {value_text(f)}. {cite(f)}")
    elif other:
        if intent in ("summary", "context"):
            lines.append("**Key findings**")
        if selection.presentation == "table" and len(other) > 1:
            lines.append("\n".join([
                "| Measure | Geography | Estimate |", "| --- | --- | --- |",
                *[f"| {label(f)} | {md(f['geography'])} | {value_text(f)} {cite(f)} |" for f in other],
            ]))
        else:
            # Geography appears once when all facts refer to the same place.
            if geography and intent not in ("context", "summary", "missing"):
                lines.append(f"**{md(geography)}**")
            lines.append("\n".join("- " + fact_line(f, not geography) for f in other))

    tenure = tenure_finding(facts)
    if tenure:
        lines.append(tenure)
    labels = " ".join(f["label"].lower() for f in facts)
    insight = None
    if selection.insight == "income_sources" and any(s in labels for s in ("social security", "supplemental security", "retirement income")):
        insight = "Income-source figures help frame research on financial security and relevant services. Receiving a benefit doesn't establish that it is someone's main income. Household totals include all ages, not individual older residents."
    elif selection.insight == "housing" and (
        any(s in labels for s in ("housing cost", "burden"))
        or any(f["unit"] == "USD" and "rent" in f["label"].lower() for f in facts)
    ):
        insight = "Read housing costs alongside income and cost burden when examining affordability. These aggregate measures don't describe the budget or circumstances of a particular household."
    elif selection.insight == "service_planning" and intent in ("summary", "context") and facts:
        insight = "This snapshot can inform which resident groups and service needs to investigate further. It doesn't measure service use, unmet demand or how conditions have changed."
    if insight:
        lines.append("**What this means**\n\n" + insight)

    explain = list(dict.fromkeys(explanations))
    for key in explain:
        # Material limits stay beside the answer. Routine details move to sources;
        # a question explicitly about uncertainty receives the explanation inline.
        if key == "moe" and selection.intent != "moe":
            methodology.append(EXPLANATIONS[key])
        elif key == "joint" and insight and selection.insight == "income_sources":
            lines.append("Separate figures can't establish a combined count of residents meeting all the requested conditions.")
        elif key == "householder":
            tenure = any(f["indicator"] in {"older_owner_households", "older_renter_households"}
                         or any(w in f["label"].lower() for w in ("owner", "renter", "tenure"))
                         for f in facts)
            if tenure:
                lines.append(EXPLANATIONS[key])
            elif not (insight and selection.insight == "income_sources"):
                lines.append("These figures count households, families or housing units, not individual residents.")
        elif key == "housing" and insight and selection.insight == "housing":
            lines.append("These figures don't establish housing instability or individual eligibility; medians cannot be combined into an average household budget.")
        elif key == "joint" and evidence.policy.get("income_dependence"):
            lines.append("Separate figures do not identify residents on fixed incomes or show whether benefits are their main income. Household benefit totals include all ages and cannot be treated as counts of older adults.")
        else:
            lines.append(EXPLANATIONS[key])
    if differences:
        methodology.extend(dict.fromkeys(d["method"] for d in differences))
    if any(f.get("method", "").startswith("derived_") for f in facts):
        lines.append("Calculated figures combine compatible source cells. Their margins of error are approximate because covariance is unavailable; source details show the inputs and formula.")
    if warnings:
        methodology.extend(warnings)
        # Preserve meaningful geographic/denominator caveats visibly, without
        # repeating generic comparison and unequal-bin warnings already explained.
        for warning in warnings:
            if not any(w in warning.lower() for w in ("descriptive", "significance", "unequal widths")):
                lines.append(warning)
            elif "neighbor" in warning.lower():
                lines.append("Neighbors share a land boundary longer than one metre in the 2022 plan; point contacts and nearby districts across water are excluded.")

    if programs:
        lines.extend(program_text(p) for p in programs)
        dates = ", ".join(sorted({p["verification_date"] for p in programs}))
        lines.append(f"Program sources were last checked **{dates}**. Eligibility rules in this directory remain incomplete; use the official links and confirm current requirements and application availability with the agency.")
    if facts:
        periods = ", ".join(dict.fromkeys(f["reference_period"] for f in facts))
        lines.append(f"Source: **American Community Survey, {md(periods)}**. ± shows the available 90% margin of error. Linked references and full statistical definitions are below.")
    if intent == "unsupported":
        lines.append("A useful next step is to identify an official source whose population, geography and time period match the question.")
    elif selection.follow_up and facts:
        if selection.follow_up == "state_comparison" and not differences and selection.active_district_id:
            lines.append("A useful next question: How does this district compare with Hawaiʻi statewide on these measures?")
        elif selection.follow_up == "age_distribution" and intent == "summary" and selection.active_district_id:
            lines.append("A useful next question: Which age groups make up the largest shares of this district?")
        elif selection.follow_up == "source_details" and intent in ("context", "missing", "moe"):
            lines.append("For a closer look, open the source details to review the population definition and the original reported values.")
    return "\n\n".join(lines), list(dict.fromkeys(methodology))
