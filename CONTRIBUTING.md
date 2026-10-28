# Contributing to DistrictIQ

Start with the [README](README.md) for setup, data scope and the verified progress checklist.

## Team workflow

1. Fetch the latest `main` and create a focused branch (for example `feature/program-rules` or `fix/source-citations`). Codex-created branches use `codex/`.
2. Keep changes focused. Preserve existing working APIs, ingestion provenance and the official 2022 district plan.
3. Run `make test`, `make lint`, and `make build`. Run populated integration tests on a disposable local database when modifying queries, models or pipelines.
4. Review `git diff` and `git diff --cached`. Run `.venv/bin/python scripts/check_secrets.py --staged --bundles` before committing.
5. Open a pull request explaining the problem, behavior, validation and remaining limits. Request a teammate review; resolve conflicts with a merge or local rebase without rewriting shared history.
6. Update README checkboxes only after implementing and verifying the feature. An unchecked **In Progress** item remains unfinished. Record evidence and limits in `docs/`.

Do not force-push shared branches, overwrite teammates' commits, or assume branch protection is configured. Repository administrators should configure required reviews and the Verify DistrictIQ check for `main` when team permissions allow.

## Data and statistical changes

- Use the existing approved CLI pipelines and metadata registry; never expose ingestion or arbitrary SQL through the assistant.
- Preserve estimates, MOEs, null/suppression markers, statistical universes, source URLs, reference periods, geographic IDs and boundary vintage.
- Add meaningful fixtures or integration checks for new definitions/calculations. Public aggregate data may be committed only with provenance and applicable source terms. Do not commit confidential or individual-level records.
- Prefer cached source captures for deterministic tests. Live source refreshes and paid model evaluations are opt-in.
- Use Alembic for additive model changes. Document rollback and compatibility concerns; never reset the shared database or delete Docker volumes to fix migrations.
- Program discovery is not an eligibility decision. Keep unresolved rules and source verification/effective dates explicit.

## Credentials and local state

Keep real credentials in ignored local environment files. Only `.env.example` belongs in Git, with empty secret fields/placeholders. Never put private credentials in `NEXT_PUBLIC_*` variables, screenshots, reports, test fixtures, URLs, commit messages or pull requests.

The source scanner detects known configured secrets and several common token patterns; manually review staged files as well. If an actual secret enters Git history, stop publishing, notify its owner without revealing it, rotate/revoke it, and coordinate any required history remediation. A later deletion does not undo exposure.

Dependency directories, caches, build output, database dumps and local research scratch work stay ignored. The small official source captures and reviewed reports are intentionally versioned for reproducibility; database volumes are not.
