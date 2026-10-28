"""Read-only final HTTP/provenance checks; no model calls or credential logging."""

import json
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]


def main():
    rows = json.loads((ROOT / "docs/research-30-question-live.json").read_text())
    checked = {}
    with httpx.Client(
        base_url="http://127.0.0.1:8000", timeout=20, trust_env=False
    ) as client:
        for path in ("/healthz", "/readyz"):
            r = client.get(path)
            assert r.status_code == 200
            checked[path] = r.json()
        assert (
            len(client.get("/v1/districts/house-30/profile").json()["statistics"]) == 46
        )
        assert (
            len(client.get("/v1/districts/senate-15/profile").json()["statistics"])
            == 46
        )
        urls = {}
        for row in rows:
            assert row["status"] == "passed_source_reconciliation"
            for citation in row["answer"]["citations"]:
                urls[citation["provenance_url"]] = citation["statistic_id"]
        for path, id in urls.items():
            assert path.startswith("/v1/")
            r = client.get(path)
            assert r.status_code == 200 and r.json()["statistic_id"] == id
        programs = client.get("/v1/programs").json()["programs"]
        assert len(programs) == 16
        for p in programs:
            r = client.get(p["provenance_url"])
            assert (
                r.status_code == 200
                and r.json()["eligibility_url"] == p["eligibility_url"]
            )
            assert r.json()["eligibility_status"] == "rules_incomplete"
        checked.update(
            {
                "resolved_statistical_provenance_urls": len(urls),
                "program_detail_urls": len(programs),
                "dashboard_profile_fields_per_district": 46,
                "benchmark_questions_checked": 30,
            }
        )
    with httpx.Client(timeout=20, trust_env=False) as client:
        checked["frontend_status"] = client.get(
            "http://127.0.0.1:3000/assistant?district=house-30"
        ).status_code
        assert checked["frontend_status"] == 200
    (ROOT / "docs/research-http-verification.json").write_text(
        json.dumps(checked, indent=2) + "\n"
    )
    print(json.dumps(checked, indent=2))


if __name__ == "__main__":
    main()
