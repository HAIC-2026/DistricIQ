"""Opt-in live model + PostgreSQL checks, including the 30-question regression matrix.

Calls the same bounded answer service directly (HTTP/browser checks are separate), avoiding
the public endpoint's per-minute interactive rate limit. No keys or connection strings logged.
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


def verify_sources(result):
    for c in result["citations"]:
        expected = observations(c["geography_id"], [c["indicator"]])[0]
        assert (c["estimate"], c["moe"], c["reference_period"]) == (
            expected["estimate"],
            expected["moe"],
            expected["reference_period"],
        )
        assert c["provenance_url"]


def verify_intent(case, result):
    codes = {c["indicator"] for c in result["citations"]}
    required = {
        2: {"older_adult_share"},
        3: {"older_poverty_count"},
        4: {"older_owner_households", "older_renter_households"},
        6: {"older_adults_living_alone"},
        8: {"housing_burden_30_plus_share"},
        9: {"household_income_under_50000"},
        13: {"B25070_010"},
        19: {"age_under_18"},
        20: {"dp02_r017_percent"},
        21: {"child_poverty_count"},
        22: {"dp02_r078_percent"},
        23: {"dp02_r052_estimate"},
    }
    if case["number"] in required:
        assert required[case["number"]] <= codes, "Requested measure missing"
    if case["number"] in {1, 4, 7, 12, 14, 15, 16, 26, 30}:
        assert result["answerability"] == "partially_answerable", (
            "Unavailable combined/statistical condition must be explicit"
        )
    if case["number"] == 10:
        assert "compare_neighbors" in result["tools_used"], (
            "Neighbors must use actual spatial adjacency"
        )
    if case["number"] in {25, 28, 29}:
        assert result["programs"], "Program information must come from the directory"
    if case["number"] == 27:
        assert result["citations"], "Needs question requires measured indicators"


async def main(benchmark, selected=None):
    if benchmark:
        cases = json.loads(
            (
                ROOT / "outputs/data-requirements/question-to-data-matrix.json"
            ).read_text()
        )["questions"]
    else:
        cases = [
            {"number": i + 1, "question": q}
            for i, q in enumerate(
                [
                    "What percentage of adults 25+ have a bachelor's degree or higher here?",
                    "How many older adults live alone here?",
                    "How many households report SNAP receipt here?",
                    "Compare this district with the state on bachelor's degree or higher attainment.",
                    "How many kupuna in my district live on fixed incomes?",
                ]
            )
        ]
    if selected:
        cases = [c for c in cases if c["number"] in selected]
    results = []
    for case in cases:
        result = None
        try:
            result = await answer(
                ChatRequest(message=case["question"], district_id="house-30")
            )
            verify_sources(result)
            if benchmark:
                verify_intent(case, result)
            if not benchmark and case["number"] == 5:
                assert result["citations"] and result["answerability"] == "partially_answerable"
                assert "fixed" in result["message"] or "primary" in result["message"]
            results.append(
                {
                    "number": case["number"],
                    "question": case["question"],
                    "status": "passed_source_reconciliation",
                    "answer": result,
                }
            )
            print(
                json.dumps(
                    {
                        "number": case["number"],
                        "status": "passed_source_reconciliation",
                        "tools": result["tools_used"],
                    }
                ),
                flush=True,
            )
        except Exception as exc:
            results.append(
                {
                    "number": case["number"],
                    "question": case["question"],
                    "status": "failed",
                    "error_type": type(exc).__name__,
                    "answer": result,
                }
            )
            print(
                json.dumps(
                    {
                        "number": case["number"],
                        "status": "failed",
                        "error_type": type(exc).__name__,
                    }
                ),
                flush=True,
            )
    out = (
        ROOT
        / "docs"
        / (
            "research-30-question-live.json"
            if benchmark
            else "research-milestone1-live.json"
        )
    )
    if selected and out.exists():
        previous = {r["number"]: r for r in json.loads(out.read_text())}
        previous.update({r["number"]: r for r in results})
        merged = [previous[n] for n in sorted(previous)]
    else:
        merged = results
    out.write_text(json.dumps(merged, indent=2, ensure_ascii=False))
    if any(r["status"] == "failed" for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--benchmark", action="store_true")
    p.add_argument(
        "--questions", help="Comma-separated benchmark question numbers to recheck"
    )
    args = p.parse_args()
    asyncio.run(
        main(
            args.benchmark,
            {int(n) for n in args.questions.split(",")} if args.questions else None,
        )
    )
