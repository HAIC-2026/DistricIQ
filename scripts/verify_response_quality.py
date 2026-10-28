"""Opt-in live qualitative scenarios, with deterministic source/format contracts.

Uses the production answer service and existing DB. Makes billed OpenAI calls;
no ingestion, database writes or exact-model-wording assertions.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "services/api"), str(ROOT)]
from app.ai.district_assistant import answer  # noqa: E402
from app.schemas.assistant import ChatRequest  # noqa: E402
from app.services.research_service import observations  # noqa: E402

CASES = [
    ("exact", "What is the population here?", "house-30"),
    ("related", "How many kupuna in my district live on fixed incomes?", "senate-15"),
    ("universe", "Are older residents in my district more likely to rent or own their homes?", "house-30"),
    ("comparison", "Compare House Districts 30 and 31 on poverty rate and median household income.", "house-30"),
    ("uncertainty", "Explain the margin of error for median household income here.", "house-30"),
    ("programs", "Which official programs support older adults with limited retirement income?", "senate-15"),
    ("unsupported", "How many residents here have been evicted in the last month?", "house-30"),
]


async def main(selected=None):
    output_path = ROOT / "docs/response-quality-live.json"
    results = json.loads(output_path.read_text()) if selected and output_path.exists() else []
    if selected:
        results = [r for r in results if r["scenario"] != selected]
    for name, question, district in CASES:
        if selected and name != selected:
            continue
        result = None
        try:
            result = await answer(ChatRequest(message=question, district_id=district))
            for c in result["citations"]:
                original = observations(c["geography_id"], [c["indicator"]])[0]
                assert (c["estimate"], c["moe"], c["reference_period"]) == (
                    original["estimate"], original["moe"], original["reference_period"]
                )
                assert c["provenance_url"] and c["source"]
                assert f"[{c['ref']}]" in result["message"]
            assert "exact requested measure is not established" not in result["message"]
            if name == "exact":
                assert len(result["citations"]) == 1
                assert result["citations"][0]["indicator"] == "population"
                assert "**" in result["message"]
            if name in ("related", "universe"):
                assert result["answerability"] == "partially_answerable"
                assert result["citations"]
            if name == "related":
                assert len(result["citations"]) <= 3
                assert not any("householder" in c["label"].lower() for c in result["citations"])
            if name == "universe":
                assert {"older_owner_households", "older_renter_households"} <= {
                    c["indicator"] for c in result["citations"]
                }
            if name == "comparison":
                assert len(result["comparisons"]) == 2 and "| Measure |" in result["message"]
            if name == "uncertainty":
                assert "90% confidence" in result["message"]
            if name == "programs":
                assert 1 <= len(result["programs"]) <= 3 and "incomplete" in result["message"]
            if name == "unsupported":
                assert result["answerability"] in ("partially_answerable", "unsupported")
                assert not any("evict" in c["indicator"] for c in result["citations"])
                assert "fixed income" not in result["message"]
            results.append({"scenario": name, "question": question, "district": district,
                            "status": "passed_source_and_response_contracts", "answer": result})
            print(name, "passed", flush=True)
        except Exception as exc:
            results.append({"scenario": name, "question": question, "district": district,
                            "status": "failed", "error_type": type(exc).__name__, "answer": result})
            print(name, "failed", type(exc).__name__, flush=True)
        results.sort(key=lambda r: [c[0] for c in CASES].index(r["scenario"]))
        output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    assert all(r["status"].startswith("passed") for r in results), "See saved scenario results"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=[c[0] for c in CASES])
    asyncio.run(main(parser.parse_args().scenario))
