"""Opt-in live API acceptance check. Uses configured OpenAI billing through FastAPI."""

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.database import session  # noqa: E402
from app.models.entities import Statistic  # noqa: E402


def post(payload):
    request = urllib.request.Request(
        "http://127.0.0.1:8000/v1/assistant/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=85) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code == 429 and attempt == 0:
                print("Rate limit observed; waiting for the next allowed request window.", flush=True)
                time.sleep(60)
                continue
            raise RuntimeError(f"HTTP {error.code}: {error.read().decode()}") from None


def verify_sources(answer):
    assert answer["citations"], "A statistical answer must have citations"
    with session() as db:
        for c in answer["citations"]:
            stored = db.get(Statistic, c["statistic_id"])
            assert stored is not None
            assert (stored.estimate, stored.moe, stored.reference_period, stored.geography_id) == (
                c["estimate"],
                c["moe"],
                c["reference_period"],
                c["geography_id"],
            )
            for key in ("workbook", "sheet", "estimate_cell", "moe_cell", "workbook_sha256"):
                assert stored.provenance.get(key) == c.get(key)
    assert "2020–2024" in answer["message"]


def main():
    history = []
    results = []
    cases = [
        ("What is the population here?", "house-30", "get_district_indicators"),
        ("And its poverty rate?", "house-30", "get_district_indicators"),
        (
            "Compare House Districts 30 and 31 on poverty rate and median household income.",
            "house-30",
            "compare_districts",
        ),
        (
            "How does Senate District 15 compare with the state on poverty rate?",
            "house-30",
            "compare_benchmark",
        ),
        ("Compare this district with Honolulu County on poverty rate.", "house-30", "compare_benchmark"),
        ("What are the biggest age groups in this district?", "house-30", "get_distribution"),
        ("What information is missing from this ACS profile?", "house-30", "explain_available_indicators"),
        ("Explain the margin of error for median household income here.", "house-30", None),
        ("What do the available housing statistics suggest?", "house-30", "get_housing_statistics"),
        ("How many residents aged 65+ live on fixed incomes?", "house-30", None),
    ]
    for index, (question, district, tool) in enumerate(cases):
        started = time.monotonic()
        answer = post({"message": question, "district_id": district, "history": history[-8:]})
        if index == 9:
            assert not answer["citations"] and not answer["comparisons"]
            assert "not available" in answer["message"]
            assert "do not identify residents on fixed incomes" in answer["message"]
        else:
            verify_sources(answer)
        if tool:
            # Profiles are also legitimate for a single core indicator.
            assert tool in answer["tools_used"] or (
                index < 2 and "get_district_profile" in answer["tools_used"]
            ), answer["tools_used"]
        geos = {c["geography_id"] for c in answer["citations"]}
        if index == 0:
            assert any(c["indicator"] == "population" and c["estimate"] == 34283 for c in answer["citations"])
        if index == 1:
            assert any(c["indicator"] == "poverty_rate" and c["estimate"] == 9.8 for c in answer["citations"])
        if index == 2:
            assert geos == {"house-30", "house-31"} and answer["comparisons"]
        if index == 3:
            assert geos == {"senate-15", "state-15"}
        if index == 4:
            assert geos == {"house-30", "county-15003"}
        if index == 5:
            assert answer["citations"][0]["label"] == "35 to 44 years"
        if index == 6:
            assert all(c["estimate"] is None for c in answer["citations"])
        history.extend(
            [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer["message"][:1200]},
            ]
        )
        results.append(
            {"question": question, "seconds": round(time.monotonic() - started, 2), "answer": answer}
        )
        print(f"PASS {index + 1}: {question} ({results[-1]['seconds']}s)", flush=True)
        (ROOT / "work/assistant-live-verification.json").write_text(
            json.dumps(results, indent=2, ensure_ascii=False)
        )
    print(
        f"{len(results)} live acceptance cases passed; all returned statistical citations reconciled with PostgreSQL."
    )


if __name__ == "__main__":
    main()
