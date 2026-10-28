# DistrictIQ research assistant expansion

Verified October 27, 2026, Pacific/Honolulu. Project: `/Users/gianvelasco/Desktop/HAIC26`.

All five requested milestones are implemented. There are **388 searchable measures**: the original 46 aliases, 123 additional reviewed profile measures, 209 native Detailed Table estimate variables and 10 reviewed calculations. Count/percentage variants and hierarchical totals are included; this is not 388 independent demographic topics or complete access to every original row.

The original **76 district geometries, 3,772 mapped statistics and 44,444 profile observations remain intact**. The dashboard profile API continues returning46 fields per geography. The expanded assistant reads the same PostgreSQL database through bounded, read-only tools.

## Completed milestones

**1 — Existing observations.** The reviewed registry exposes educational attainment, school enrollment, disability by broad age, SNAP, Social Security/retirement/SSI/cash-assistance receipt, grandparents responsible, broadband/computers, household composition, older adults living alone, commuting, vehicles, insurance, crowding and age-specific poverty rates. Definitions specify worksheet/row, measure role, unit, universe and denominators. Original count/MOE or percent/percent-MOE cells and suppression markers are retained. Workbook row numbers are not treated as Census variable IDs.

Milestone 1 passed backend/database/frontend checks and five live questions before new statistical imports. See `research-milestone1-live.json`. Education, SNAP, older-alone and state comparisons came from existing PostgreSQL observations; fixed-income questions received explicitly limited context.

**2 — Discovery and complex questions.** Metadata/synonym search ranks approved labels, universes and topics, including kūpuna terminology. It searches the reviewed registry and approved native table metadata; no canned statistical answers, embeddings or vector database were introduced. Existing indicator/comparison tools can also resolve the new approved IDs.

The server renders facts, numbers and citations. It validates counts versus percentages, requires the50%+ cell for severe rent burden, requires approved sum recipes, and uses PostGIS for neighbors. Compound quantitative conditions are checked against retrieved measure dimensions; unrelated marginals cannot become a joint or unduplicated count. Unavailable hardship, primary-income dependence, instability, eligibility, county-remainder and trend measures are explicitly contextual. Household/householder alternatives are distinguished from person measures. Tool-selection mismatches can request corrected evidence; invented references fail closed.

The10 calculations cover older adults living alone; households below $50,000;30%+ housing burden count/share; owner-household share; older/child poverty counts; older-householder owner/renter counts; and older-householder income below $50,000. Calculations use compatible cells and documented MOE approximations, never arbitrary model formulas, multiplied marginals or subtracted medians.

**3 — Five official tables.** All were acquired directly for 51 House districts, 25 Senate districts,five counties and Hawaiʻi statewide, reference period 2020–2024. Each table was validated before proceeding to the next. No geographic crosswalking was used.

| Table / verified metadata | Pairs per geography | House | Senate | County | State | Total records |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| [B17001: poverty by sex/age](https://api.census.gov/data/2024/acs/acs5/groups/B17001.html) |59|3,009|1,475|295|59|4,838|
| [B25070: rent/income share](https://api.census.gov/data/2024/acs/acs5/groups/B25070.html) |11|561|275|55|11|902|
| [B25007: tenure/householder age](https://api.census.gov/data/2024/acs/acs5/groups/B25007.html) |21|1,071|525|105|21|1,722|
| [B25011: tenure/type/householder age](https://api.census.gov/data/2024/acs/acs5/groups/B25011.html) |49|2,499|1,225|245|49|4,018|
| [B19037: householder age/income](https://api.census.gov/data/2024/acs/acs5/groups/B19037.html) |69|3,519|1,725|345|69|5,658|
| **Total** |**209**|**10,659**|**5,225**|**1,045**|**209**|**17,138**|

All17,138 estimate fields in this acquisition are numeric. Native annotations and MOE availability remain separate. Exact returned identifiers match lower-chamber001–051, upper-chamber001–025, state 15 and all five county codes. Full Census `GEO_ID` strings, original geographic labels, variable IDs, universes and 2024/2022 plan compatibility are preserved. Metadata establishes B25070's universe as **renter-occupied housing units**, with a separate not-computed cell; it must not be relabeled as all renter individuals. Native metadata supersedes any broader research-stage description.

Raw metadata and four geographic captures per table are in `data/raw/acs/2024/detailed/<table>/`. Captures retain original values, annotations, retrieval dates, hashes and request parameters excluding the key. Separate `acs-2024-detailed-<table>` source namespaces protect workbook records. Every estimate/MOE was reconciled with its capture. All five cached reimports were verified as idempotent.

The initially rejected key was corrected through activation. Successful Census group responses include `NAME` automatically; the importer uses `group(<table>)` to avoid duplicated headers and rejects incomplete schemas/geographies before committing.

**4 — Retrieval and comparisons.** Native variables participate in the same search/retrieval layer as profile observations and recipes. Comparisons check definitions, units, periods and boundary plans. Derived provenance includes every input. Native provenance uses the existing statistics endpoint; profile/recipe provenance uses the research endpoint.

`compare_neighbors` uses same-chamber2022 polygons sharing a land boundary longer than one projected metre, excluding point contacts and across-water proximity. House 30's verified neighbors are House 28,29,31 and 32. County/state rules are preserved, including separate Maui/Kalawao regional contexts. Differences are descriptive; no significance or difference-MOE claim is added.

**5 — Program directory.** Migration`0003` adds only `government_programs`. Sixteen reviewed records cover SNAP,SSI,AABD,Med-QUEST,Medicare Savings/Extra Help,aging/Kūpuna Care,H-HEAP,housing programs/property inventory,WIC,TANF,childcare subsidy andPOD. Records preserve agency, purpose, population, reported criteria, service area, official application/documentation, verification date, effective-rule notes, availability and unresolved criteria. Their actual source-review date remains **October 26,2026**. All have explicit `rules_incomplete` status; this is not an eligibility engine or a live enrollment feed.

Program search/details and UI source cards provide official links, dates and warnings. A closed HPHA waitlist remains closed in the dated directory; an application link does not promise capacity or approval. Import is idempotent and refuses to replace newer verification with older records. No RAG, administrative participation integration or individual qualification inference was added.

## Actual database-backed examples

House District 30, ACS 2020–2024:

| Measure | Estimate |90% MOE|Basis|
| --- | ---: | ---: | --- |
|People 65+ below poverty|518|approximately 150.8|Four B17001 cells; poverty-status universe|
|Children under 18 below poverty|1,045|approximately 261.1|Twelve disjoint B17001 cells|
|Renter households in50%+ rent-burden bin|1,467|284|Direct B25070_010E/M|
|Owner households with householder 65+|815|approximately 177.7|Three B25007 age bins|
|Renter households with householder 65+|774|approximately 156.2|Three B25007 age bins|
|Older-householder households below $50,000|579|approximately 151.9|B19037 income-bin sum|

Derived MOEs use documented RSS/subset approximations with covariance unavailable. Householder income/tenure is not every older resident's income/tenure. Values above were read from PostgreSQL, not hardcoded into production.

## APIs, bounds and configuration

Added read-only APIs:

- `GET /v1/research/indicators?q=<query>&limit=10`
- `GET /v1/research/observations/{geography_id}/{indicator_id}`
- `GET /v1/research/observations/{geography_id}/{indicator_id}/provenance`
- `GET /v1/programs?q=<query>&limit=16`
- `GET /v1/programs/{program_id}`

Existing assistant, dashboard, source, geometry and comparison APIs remain. `search_indicators`, `get_observations`, `compare_observations`, `compare_neighbors`, `search_programs` and `get_program` extend the existing read-only tool set. No arbitrary SQL or database mutation tools are model-facing.

Both configured keys remain server-side in the ignored `.env`. Captures/provenance exclude Census key parameters. The recorded scan found neither OpenAI nor Census key in checked public build assets/captures. Existing body/rate/concurrency/history restrictions remain. The model loop permits eight rounds/seven data-tool calls under the existing 65-second deadline. Short pytest traces reduce connection-detail exposure on failures.

The existing SDK and response rendering follow the [official function-calling contract](https://developers.openai.com/api/docs/guides/function-calling); no model migration or new dependency was needed.

## Evaluation and verification

All30 representative questions passed the final live source-reconciliation run and configured expected-measure/limitation assertions. **This does not mean30 exact statistical answers exist.** Results: **9 direct statistical answers, 8 supported calculations/comparisons, 3 program-information answers and 10 partial/contextual answers**. No empty unsupported fallback occurred in this run; unsupported exact intersections remain unsupported within contextual answers.

See [the question-by-question evaluation](research-30-question-evaluation.md), [complete live responses](research-30-question-live.json), and [database verification](research-implementation-verification.json). Live evaluation uses the same bounded answer service with the configured model and PostgreSQL. HTTP/browser interaction checks are separate. Every selected value/MOE is reconciled with its stored source; assertions cover key counts, percentages, recipes, neighbor use, programs and explicit limitations. Early runs exposed real-but-insufficient measure selection; guards were added and affected cases rerun.

|Check|Final result|
| --- | --- |
|Backend tests, including real PostgreSQL/PostGIS|**137 passed**|
|Frontend tests|**17 passed**|
|Combined automated tests|**154 passed**|
|Ruff|Passed|
|Frontend lint/TypeScript|Passed; repository lint runs TypeScript|
|Production Next.js build|Passed|
|Python compilation|Passed|
|Original worksheet/statistic and 76-district regression|Passed|
|Every native estimate/MOE, geography, hash and GEO_ID|Reconciled|
|Idempotence|All five tables and program directory verified|

One non-failing existing Starlette/httpx TestClient deprecation warning remains. Browser checks cover production page loading, House 30 education and original cells, new child-poverty retrieval, fixed-income contextual limitations, Senate 15 program discovery and expandable official source/application controls. Final HTTP/source/browser evidence accompanies this report. This is targeted interaction testing, not a cross-browser/accessibility certification or universal proof of natural-language correctness.

## Files

Created:

- Backend: `analytics/research_indicators.py`, `services/research_service.py`, `services/program_service.py`, `ai/answer_policy.py`, `api/v1/research.py`, `api/v1/programs.py` under `services/api/app/`.
- Migration: `services/api/alembic/versions/0003_government_programs.py`.
- Ingestion: `pipelines/census/detailed.py`, `pipelines/programs/__init__.py`, `pipelines/programs/ingest.py`, `data/manifests/government-programs.json`.
- Verification: `scripts/verify_research_assistant.py`, `scripts/verify_research_http.py`; backend `test_research.py`, `test_detailed_tables.py`, `test_programs.py`, `test_answer_policy.py`.
- Raw official captures/metadata in the five table folders; reports, responses and verification artifacts under `docs/`.

Modified:

- Backend `ai/district_tools.py`, `ai/district_assistant.py`, `schemas/assistant.py`, `models/entities.py`, `services/district_service.py`, `core/http.py`, `main.py`.
- Existing backend tests `test_assistant.py`, `test_postgis.py` and `services/api/pyproject.toml`.
- Frontend `components/assistant/Assistant.tsx`, `types/assistant.ts`, `tests/assistant.test.tsx`.
- `scripts/cli.py`, `Makefile`, `README.md`.

Original workbook/geometry files, dashboard layout, ArcGIS components, existing migrations and ingestion paths were preserved. No Docker volume was deleted.

## Remaining limits and next steps

There is no current configuration/import blocker. Both keys are configured and all five tables are acquired. Remaining scope limits:

1. No verified district primary-Social-Security-dependence count or full older/alone/renter/primary-income intersection. Related household receipt is contextual.
2. No exact basic-needs hardship, instability, individually eligible or underserved population count from marginal ACS statistics; no remainder medians by subtraction.
3. One2020–2024 period does not supply trends. Not all 542 original profile row definitions have reviewed retrieval semantics.
4. Search is bounded metadata/synonym ranking. New definitions/recipes need review; model selection remains nondeterministic and can be suboptimal. Citations, universes and evaluation remain essential.
5. Program exceptions, thresholds, effective versions, live capacity and district administrative enrollment remain incomplete. Directory records are dated discovery information, not individual screening.
6. Approximate MOEs do not establish general significance, allocation uncertainty or a new reliability-threshold policy.

Next: review additional profile semantics and paraphrase tests, curate program-rule versions/status refreshes, then add other tables only for demonstrated gaps. RAG, PUMS district estimates and crosswalking are not prerequisites.

## Restart commands

The database, backend and verified production frontend were started and left running for review at `http://localhost:3000/assistant?district=house-30`.

Later, from the project directory:

```bash
cd /Users/gianvelasco/Desktop/HAIC26
docker compose up -d db
make migrate
```

In separate terminals from that directory:

```bash
make dev-api
```

```bash
make dev-web
```

Production alternative: `npm --prefix apps/web run build`, then `npm --prefix apps/web run start`. Do not start a second frontend on port 3000. Restarting requires no reimport.

Developer-only repeatable imports: `make ingest-detailed TABLE=B17001` or another approved table, and `make ingest-programs`. Cached captures are reused; CLI`--live` explicitly requests remote refresh. `make verify-research` performs billed live model calls.

Final HTTP evidence: [service and citation checks](research-http-verification.json). Visual evidence: [verified Senate15 answer and source disclosure](research-assistant-verified.png).
