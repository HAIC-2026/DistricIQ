from app.discovery.dataset_ranker import evaluate, rank
from app.schemas.discovery import Dataset, Purpose

PURPOSE = Purpose(chamber="house")


def test_real_official_metadata_scores_reproducibly(official_house):
    a = evaluate(official_house, PURPOSE)
    b = evaluate(official_house, PURPOSE)
    assert a.model_dump() == b.model_dump()
    assert a.score == 100
    assert sum(c.maximum for c in a.categories) == 100
    assert a.status == "valid_candidate"
    assert rank([official_house], PURPOSE)[0].status == "recommended"


def test_authority_beats_an_equivalent_unverified_copy(official_house):
    other = official_house.model_copy(
        update={"service_url": "https://example.com/FeatureServer/0", "dataset_id": "copy"}
    )
    results = rank([other, official_house], PURPOSE)
    assert results[0].dataset.dataset_id == official_house.dataset_id
    assert results[1].score < results[0].score


def test_wrong_chamber_rejected(official_house):
    e = evaluate(official_house, Purpose(chamber="senate"))
    assert e.status == "rejected"
    assert any("chamber" in r.lower() for r in e.rejections)


def test_outside_hawaii_rejected(official_house):
    e = evaluate(official_house.model_copy(update={"geographic_coverage": "-125,32,-114,42"}), PURPOSE)
    assert e.status == "rejected"
    assert any("outside Hawaiʻi" in r for r in e.rejections)


def test_vintage_not_inferred_from_modified_date(official_house):
    d = official_house.model_copy(update={"geographic_vintage": 2012, "modified_date": "2026-10-26"})
    assert evaluate(d, PURPOSE).status == "rejected"


def test_missing_required_fields_rejected(official_house):
    e = evaluate(official_house, Purpose(chamber="house", required_fields=["B19013_001E"]))
    assert e.status == "rejected"
    assert any("B19013_001E" in r for r in e.rejections)


def test_missing_evidence_cannot_be_recommended():
    d = Dataset(dataset_id="unknown", title="Official House Districts 2026")
    e = rank([d], PURPOSE)[0]
    assert e.status == "insufficient_evidence"
    assert e.score == 0
    assert d.reference_year is None


def test_duplicate_district_identifiers_fail(official_house):
    i = dict(official_house.inspection)
    i["verified_identifiers"] = [1] * 51
    assert evaluate(official_house.model_copy(update={"inspection": i}), PURPOSE).status == "rejected"
