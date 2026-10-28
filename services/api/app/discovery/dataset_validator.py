from urllib.parse import urlsplit

from app.schemas.discovery import Dataset, Purpose


def validate(dataset: Dataset, purpose: Purpose) -> tuple[list[str], list[str]]:
    rejected: list[str] = []
    missing: list[str] = []
    i = dataset.inspection or {}
    if dataset.access_level and dataset.access_level != "public":
        rejected.append("Public access is not established")
    if dataset.access_level is None:
        missing.append("Catalog public access declaration is missing")
    if dataset.service_url and urlsplit(dataset.service_url).hostname != "geodata.hawaii.gov":
        missing.append("Service publisher requires independent provenance review")
    if dataset.license and "use prohibited" in dataset.license.lower():
        rejected.append("License prohibits use")
    if not dataset.license:
        missing.append("License evidence is missing")
    if (
        purpose.geographic_level
        and dataset.geographic_level
        and purpose.geographic_level != dataset.geographic_level
    ):
        rejected.append("Incompatible geographic level")
    if purpose.chamber and dataset.geographic_level and purpose.chamber != dataset.geographic_level:
        rejected.append("Wrong legislative chamber or geographic level")
    if dataset.validation_status == "invalid_service":
        rejected.append("Underlying service is invalid for the requested use")
    if purpose.category == "boundary":
        if dataset.validation_status != "service_inspected":
            missing.append("Underlying service could not be sufficiently inspected")
        else:
            if i.get("geometry_type") != "esriGeometryPolygon" or not i.get("queryable"):
                rejected.append("Queryable polygon geometry is required")
            name = str(i.get("name", "")).lower()
            if purpose.chamber and f"state {purpose.chamber}" not in name:
                rejected.append("Layer name does not verify the requested chamber")
            vintage = i.get("geographic_vintage")
            if purpose.boundary_vintage and vintage and vintage != purpose.boundary_vintage:
                rejected.append("Service boundary vintage is incompatible")
            if purpose.boundary_vintage and not vintage:
                missing.append("Service boundary vintage is unknown")
            expected = {"house": 51, "senate": 25}.get(purpose.chamber)
            if expected:
                if i.get("feature_count") != expected:
                    rejected.append("Feature count does not match expected chamber count")
                try:
                    actual = sorted(int(x) for x in i.get("verified_identifiers", []))
                except (TypeError, ValueError):
                    actual = []
                if actual != list(range(1, expected + 1)):
                    rejected.append("Complete, unique district identifiers are not verified")
        if (
            purpose.boundary_vintage
            and dataset.geographic_vintage
            and dataset.geographic_vintage != purpose.boundary_vintage
        ):
            rejected.append("Catalog boundary vintage is incompatible")
    if purpose.required_fields:
        absent = sorted(set(purpose.required_fields) - set(dataset.available_fields))
        if absent:
            (rejected if dataset.validation_status == "service_inspected" else missing).append(
                "Required fields missing: " + ", ".join(absent)
            )
    # Geographic extent from service is projected; use catalog WGS84 bounds for coverage rejection.
    coverage = dataset.geographic_coverage
    if coverage and "," in coverage and not coverage.startswith("{"):
        try:
            west, south, east, north = [float(x) for x in coverage.split(",")]
            if east < -179 or west > -154 or north < 18 or south > 30:
                rejected.append("Dataset extent is outside Hawaiʻi")
        except ValueError:
            missing.append("Catalog geographic coverage could not be interpreted")
    return rejected, missing
