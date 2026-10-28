import pytest

from app.analytics.acs_profiles import PROFILE_INDICATORS
from app.core.config import ROOT
from pipelines.census.workbooks import geography_id, parse_workbook, reported_number


@pytest.fixture(scope="module")
def house_profile():
    return parse_workbook(ROOT / "data/raw/acs/acs2024_5yr_house_hi.xlsx", "house")


def test_house30_matches_published_cells_and_moe(house_profile):
    records = {s["indicator"]: s for s in house_profile["statistics"] if s["geography_id"] == "house-30"}
    for code, estimate, moe, cell in [
        ("population", 34283, 1935, "DN4"),
        ("median_household_income", 90180, 9512, "DN70"),
        ("poverty_rate", 9.8, 2.6, "DP138"),
        ("median_age", 34.9, 0.8, "DN21"),
        ("median_gross_rent", 2481, 233, "DN152"),
    ]:
        assert records[code]["estimate"] == estimate
        assert records[code]["moe"] == moe
        assert records[code]["provenance"]["estimate_cell"] == cell
        assert records[code]["reference_period"] == "2020–2024"
    assert records["poverty_population"]["estimate"] is None
    assert records["poverty_denominator"]["estimate"] is None
    assert records["older_adult_share"]["estimate"] == 11.2
    assert records["age_65_plus"]["estimate"] == 3848


def test_native_brackets_are_preserved_and_reconcile(house_profile):
    records = [s for s in house_profile["statistics"] if s["geography_id"] == "house-30"]
    age = [s for s in records if s["provenance"]["display_group"] == "age_distribution"]
    income = [s for s in records if s["provenance"]["display_group"] == "income_distribution"]
    assert len(age) == 13
    assert sum(s["estimate"] for s in age) == 34283
    assert len(income) == 10
    assert sum(s["estimate"] for s in income) == 8609
    assert not any(s["indicator"] == "age_18_34" for s in records)
    assert len(records) == len(PROFILE_INDICATORS)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("0", 0),
        ("±0", 0),
        ("9.8%", 9.8),
        ("1,935", 1935),
        ("*****", None),
        ("-", None),
        ("**", None),
        ("N", None),
        ("4,000+", None),
        ("(X)", None),
    ],
)
def test_reported_markers_are_not_zero(raw, expected):
    assert reported_number(raw) == expected


def test_geography_labels_are_strict():
    assert geography_id("State House District 30 (2024); Hawaii", "house") == "house-30"
    assert geography_id("Honolulu County, Hawaii", "county") == "county-15003"
    with pytest.raises(ValueError):
        geography_id("State Senate District 30 (2024); Hawaii", "house")


def test_worksheet_definitions_checked_before_import(tmp_path):
    import openpyxl

    path = ROOT / "data/raw/acs/acs2024_5yr_state_hi.xlsx"
    book = openpyxl.load_workbook(path)
    book["DP05"]["A4"] = "Changed definition"
    modified = tmp_path / "changed.xlsx"
    book.save(modified)
    book.close()
    with pytest.raises(ValueError, match="definition changed"):
        parse_workbook(modified, "state")
