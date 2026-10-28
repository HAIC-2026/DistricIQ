from urllib.parse import urlsplit

from app.discovery.dataset_validator import validate
from app.schemas.discovery import CategoryScore, Dataset, Evaluation, Purpose

RUBRIC = {
    "authority": 25,
    "geography": 20,
    "vintage": 15,
    "schema": 15,
    "completeness": 10,
    "access": 10,
    "methodology": 5,
}


def evaluate(dataset: Dataset, purpose: Purpose) -> Evaluation:
    i = dataset.inspection or {}
    rejected, missing = validate(dataset, purpose)
    categories: list[CategoryScore] = []

    def score(name, points, evidence):
        categories.append(
            CategoryScore(criterion=name, points=points, maximum=RUBRIC[name], evidence=evidence)
        )

    official = bool(dataset.service_url and urlsplit(dataset.service_url).hostname == "geodata.hawaii.gov")
    inspected = dataset.validation_status == "service_inspected"
    score(
        "authority",
        25 if official and i.get("credits") else 10 if official else 0,
        i.get("credits") or "Official state service hostname" if official else "Authority not verified",
    )
    compatible = bool(purpose.chamber and f"state {purpose.chamber}" in i.get("name", "").lower())
    score(
        "geography",
        20
        if compatible
        else 10
        if purpose.geographic_level and dataset.geographic_level == purpose.geographic_level and inspected
        else 0,
        i.get("name") or "Underlying geographic level not verified",
    )
    vintage = i.get("geographic_vintage")
    score(
        "vintage",
        15 if purpose.boundary_vintage and vintage == purpose.boundary_vintage else 0,
        f"Verified boundary vintage: {vintage}; required: {purpose.boundary_vintage}. Modification date is not a reference year.",
    )
    valid_fields = (
        inspected
        and i.get("identifier_field")
        and set(purpose.required_fields) <= set(dataset.available_fields)
    )
    score(
        "schema",
        15 if valid_fields else 0,
        "Verified identifier and required fields" if valid_fields else "Required schema not verified",
    )
    expected = {"house": 51, "senate": 25}.get(purpose.chamber)
    ids = i.get("verified_identifiers", [])
    complete = bool(
        expected and len(ids) == expected and len(set(ids)) == expected and i.get("feature_count") == expected
    )
    score(
        "completeness",
        10 if complete else 0,
        f"Queried {i.get('feature_count')} features; {len(ids)} identifiers; expected {expected}",
    )
    public = dataset.access_level == "public" and inspected
    license_ok = bool(dataset.license and "public domain" in dataset.license.lower())
    score(
        "access",
        (5 if public else 0) + (5 if license_ok else 0),
        "Public access verified; public-domain declaration present"
        if public and license_ok
        else "Access/license evidence incomplete",
    )
    methodology = bool(i.get("description") and "reapportionment commission" in i["description"].lower())
    score(
        "methodology",
        5 if methodology else 0,
        "Reapportionment adoption documented" if methodology else "Methodology requires review",
    )
    limitations = missing + [
        "A recommendation is not approval for ingestion.",
        "Geometry metadata does not establish the presence of demographic variables.",
    ]
    status = "rejected" if rejected else "insufficient_evidence" if missing else "valid_candidate"
    return Evaluation(
        dataset=dataset,
        score=sum(c.points for c in categories),
        categories=categories,
        status=status,
        positives=[c.evidence for c in categories if c.points == c.maximum],
        limitations=limitations,
        rejections=rejected,
        ingestion_method="Approved-manifest ArcGIS query → WGS84 validation → transactional PostGIS upsert",
    )


def rank(datasets: list[Dataset], purpose: Purpose) -> list[Evaluation]:
    order = {"valid_candidate": 0, "insufficient_evidence": 1, "rejected": 2}
    results = sorted(
        (evaluate(d, purpose) for d in datasets),
        key=lambda e: (order[e.status], -e.score, e.dataset.dataset_id),
    )
    if results and results[0].status == "valid_candidate":
        results[0].status = "recommended"
    return results
