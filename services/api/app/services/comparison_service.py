from app.services.district_service import get_district, statistics


def compare_state(district_id: str):
    return {
        "district": get_district(district_id),
        "district_statistics": statistics(district_id),
        "benchmarks": [{"geography_id": "state-15", "name": "Hawaiʻi", "statistics": statistics("state-15")}],
        "caution": "Overlapping ACS estimates are not independent. Differences are descriptive; no significance claim.",
    }


def compare_county(district_id: str):
    d = get_district(district_id)
    mapping = {
        "HAWAII": [("001", "Hawaiʻi County")],
        "HONOLULU": [("003", "Honolulu County")],
        "OAHU": [("003", "Honolulu County")],
        "KAUAI": [("007", "Kauaʻi County")],
        "MAUI": [("009", "Maui County"), ("005", "Kalawao County")],
    }
    counties = mapping.get(d["county"], [])
    return {
        "district": d,
        "district_statistics": statistics(district_id),
        "benchmarks": [
            {"geography_id": "county-15" + code, "name": name, "statistics": statistics("county-15" + code)}
            for code, name in counties
        ],
        "supplemental_benchmarks": (
            [
                {
                    "geography_id": "county-group-maui-kalawao",
                    "name": "Maui + Kalawao (DBEDT combined)",
                    "statistics": statistics("county-group-maui-kalawao"),
                }
            ]
            if d["county"] == "MAUI"
            else []
        ),
        "comparison_rule": "Official district layer county/island attribute. OAHU maps to Honolulu County. MAUI supplies separate Maui and Kalawao regional benchmarks because no county-intersection dataset was supplied. No claim of exact county overlap or population allocation.",
        "caution": "County figures are independent contextual benchmarks, never assigned to district residents. Maui and Kalawao are shown separately for the Maui region; no combined estimate is calculated.",
    }
