> These foundational procedures remain available. Current assistant, source reconciliation and full cached-data setup are documented in the [README](../README.md#test-and-verification-commands) and [response-quality report](response-quality-report.md). GitHub workflow execution is separate from local verification.

# Verification procedures

```bash
make test
make lint
make build
make test-integration  # migrated disposable PostGIS required
make validate-geography
make validate-statistics
make validate-crosswalk
```

Backend unit and API-contract tests cover actual DCAT and layer captures, pagination, deduplication, retries, stale snapshot fallback, unavailable catalogs, safe destinations, redirect/size rejection, rubric invariants, chamber/vintage/field incompatibility, complete IDs, null/sentinel values, variable/MOE preservation, poverty calculations, actual DBEDT parsing, crosswalk conservation and invalid/non-additive allocations.

AI tests use an explicitly mocked official SDK response sequence. They verify strict Pydantic tool schemas, unregistered-tool rejection, the function-call/output loop and refusal to display invented dataset IDs. They do not verify a live paid model call.

Frontend tests use synthetic statistics strictly inside test fixtures and real captured discovery evidence. They verify all district options, chamber/district request changes, empty-data cards, source-dialog opening, dataset schema inspection and the non-destructive plan. Browser verification independently confirmed the actual database-outage message and live discovery behavior.

PostGIS integration tests are opt-in through `RUN_POSTGIS_TESTS=1`; the Make target sets that variable explicitly. They check database connectivity, PostGIS, migration version, spatial coverage and coordinate round-trip. The GitHub Actions workflow provisions PostGIS; that workflow has not been run on GitHub in this session.

Manual browser checklist: public map loads with attribution; House/Senate toggle changes IDs; selected polygon highlights; live discovery produces a current candidate; field schema dialog traps focus and closes with Escape; wrong-vintage alternatives are labelled; safe plan shows validations; district-income search separates statistics from geometry; missing database/statistics remain unavailable. The implementation report records which checks actually ran and which remain pending.
