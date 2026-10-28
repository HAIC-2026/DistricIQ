"""Developer-only commands. No public HTTP mutation endpoint exists."""

import argparse
import asyncio
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "services/api"), str(ROOT)]
from app.discovery.dataset_ranker import evaluate  # noqa: E402
from app.discovery.workflow import workflow  # noqa: E402
from app.schemas.discovery import DiscoveryRequest, Purpose  # noqa: E402
from pipelines.geography.ingest import fingerprint  # noqa: E402


async def run(args):
    if args.command == "ingest-programs":
        from pipelines.programs.ingest import ingest

        return ingest()
    if args.command == "ingest-detailed":
        from pipelines.census.detailed import ingest_table

        return await ingest_table(args.table, refresh=args.live)
    if args.command in ("discover-data", "rank-datasets"):
        return await workflow.discover(DiscoveryRequest(query=args.query, limit=8))
    if args.command == "inspect-gis":
        manifest = json.loads((ROOT / "data/manifests/sources.json").read_text())
        return {
            c: await workflow.inspector.inspect(s["url"], refresh=True)
            for c, s in manifest["sources"].items()
        }
    if args.command == "approve-source":
        path = ROOT / "data/manifests/sources.json"
        manifest = json.loads(path.read_text())
        source = manifest["sources"][args.chamber]
        candidates = await workflow.catalog.search_datasets(
            f"state {args.chamber} districts", 20
        )
        candidate = next(
            (c for c in candidates if c.service_url == source["url"]), None
        )
        if candidate is None:
            raise ValueError("Candidate absent from official catalog")
        candidate = await workflow.inspector.enrich(candidate)
        evaluation = evaluate(candidate, Purpose(chamber=args.chamber))
        if evaluation.status != "valid_candidate":
            raise ValueError(
                "Source failed verification: "
                + json.dumps(evaluation.model_dump(mode="json"))
            )
        source.update(
            {
                "status": "approved",
                "approved_by": "local_developer_cli",
                "rationale": args.rationale,
                "approved_at": datetime.now(UTC).isoformat(),
                "metadata_fingerprint": fingerprint(candidate.inspection),
                "dataset_id": candidate.dataset_id,
                "evaluation": evaluation.model_dump(mode="json"),
            }
        )
        path.write_text(json.dumps(manifest, indent=2))
        return {
            "chamber": args.chamber,
            "status": "approved",
            "score": evaluation.score,
        }
    if args.command == "approve-dbedt":
        from pipelines.dbedt.ingest import URL, capture

        content, records = await capture()
        manifest = {
            "status": "approved",
            "url": URL,
            "sha256": hashlib.sha256(content).hexdigest(),
            "approved_by": "local_developer_cli",
            "rationale": args.rationale,
            "reference_date": "2024-07-01",
            "approved_at": datetime.now(UTC).isoformat(),
            "records": records,
        }
        (ROOT / "data/manifests/dbedt.json").write_text(json.dumps(manifest, indent=2))
        return manifest
    if args.command in ("ingest-geography", "ingest-acs", "ingest-dbedt"):
        if args.command == "ingest-geography":
            from pipelines.geography.ingest import ingest
        elif args.command == "ingest-acs":
            from pipelines.census.ingest import ingest
        else:
            from pipelines.dbedt.ingest import ingest
        if args.command == "ingest-acs":
            return await ingest(live=args.live)
        if args.command == "ingest-geography":
            return await ingest(refresh=args.live)
        return await ingest()
    if args.command in ("validate-geography", "validate-statistics"):
        from pipelines.quality.validate import geography, statistics

        return geography() if args.command == "validate-geography" else statistics()
    if args.command == "validate-crosswalk":
        from pipelines.crosswalk.validate import run

        return run()
    raise ValueError("Unknown command")


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "command",
    choices=[
        "discover-data",
        "rank-datasets",
        "inspect-gis",
        "approve-source",
        "approve-dbedt",
        "ingest-geography",
        "ingest-acs",
        "ingest-dbedt",
        "validate-geography",
        "validate-statistics",
        "validate-crosswalk",
        "ingest-detailed",
        "ingest-programs",
    ],
)
parser.add_argument(
    "--live",
    action="store_true",
    help="Opt in to remote refresh; local files are the default",
)
parser.add_argument(
    "--query", default="Find the best official Hawaii State House district boundaries"
)
parser.add_argument(
    "--table",
    choices=["B17001", "B25070", "B25007", "B25011", "B19037"],
    default="B17001",
)
parser.add_argument("--chamber", choices=["house", "senate"], default="house")
parser.add_argument(
    "--rationale",
    default="Verified official metadata, complete district identifiers, expected counts and documented 2022 reapportionment plan.",
)
if __name__ == "__main__":
    try:
        print(json.dumps(asyncio.run(run(parser.parse_args())), indent=2, default=str))
    except Exception as exc:
        # SQLAlchemy errors may carry connection strings. Do not echo their repr or arbitrary exception text.
        from sqlalchemy.exc import SQLAlchemyError

        message = (
            "Database unavailable; start PostgreSQL and migrate before ingestion."
            if isinstance(exc, SQLAlchemyError)
            else str(exc)
        )
        print(
            json.dumps({"error": type(exc).__name__, "message": message}),
            file=sys.stderr,
        )
        raise SystemExit(1)
