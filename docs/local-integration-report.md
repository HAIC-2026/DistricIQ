# DistrictIQ Hawaiʻi — local integration report

Verified on October 26, 2026, Hawaiʻi time, in `/Users/gianvelasco/Desktop/HAIC26`.

The core application is running at **http://localhost:3000**, with FastAPI at **http://localhost:8000** and PostgreSQL/PostGIS in Docker. The existing application, models, migration chain, ingestion commands, ArcGIS components and dashboards were extended. The selected checkout was initially empty apart from `.git`; the previous DistrictIQ implementation was recovered from the earlier local deliverable before making these changes. No additional statistical or GIS dataset was downloaded for this integration.

## 1. Docker

- Docker engine **29.9.2** and Compose **5.6.1** responded successfully.
- Container **`haic26-db-1`** is running and healthy; `pg_isready` succeeds.
- The existing `postgis/postgis:17-3.5` image runs with `platform: linux/amd64` on this Apple Silicon Mac. This configuration was successfully exercised.
- The database persists in **`haic26_pgdata`**. No previous Docker containers or volumes existed when inspected; no volume was removed or reset.
- A sandbox Keychain-helper issue during the initial public image pull was resolved with a project-local anonymous Docker config. Global credentials were not changed. The image is cached, and ordinary `docker compose up -d db` now succeeds.
- Docker Desktop needs no manual action now. After a future Mac restart, open Docker Desktop and wait until its engine is running before starting Compose.

## 2. PostgreSQL and PostGIS

Actual SQL returned **PostgreSQL 17.5**, **PostGIS 3.5.2** and GEOS 3.9.0. The PostGIS extension is enabled. Native FastAPI connects through localhost port 5432; Compose API/migration services retain the existing `db` hostname override. Published database/application ports bind loopback.

The current verified arrangement uses Docker for the database and native Python/Node processes for FastAPI and Next.js. The full Compose API/web image build workflow remains available but was not exercised in this session.

## 3. Database migrations

`make migrate` applied the actual Alembic migrations to the running database. SQL confirms **`alembic_version = 0002`**. The frozen `0002` migration adds the original ACS profile observation table without replacing the earlier schema.

Confirmed tables: `districts`, `statistics`, `sources`, `acs_profile_observations`, `crosswalk_weights`, `evaluations`, `alembic_version` and PostGIS `spatial_ref_sys`.

Both actual HTTP endpoints return **200**: `/healthz` reports `ok`; `/readyz` reports PostgreSQL ready and `postgis: true`. `ai_configured: false` does not prevent the core dashboard from working.

## 4–5. Legislative polygons

| Chamber | Imported polygons | Distinct identifiers | Plan / storage CRS |
| --- | ---: | ---: | --- |
| House | 51 | 51 | 2022 / EPSG:4326 |
| Senate | 25 | 25 | 2022 / EPSG:4326 |
| Total | **76** | **76** | |

The existing official GeoJSON captures are in `data/raw/geography/`. The original district fields, service URLs, metadata, original service CRS EPSG:3750, local capture checksum and plan vintage are preserved. IDs use the existing consistent convention, including `house-01`, `house-30` and `senate-15`.

PostGIS confirms all 76 geometries are valid and nonempty. The ingestion validator confirms exact district number sets, SRID and vintage. A same-chamber intersection audit found no pairwise overlap above 1 square metre; maximum House overlap was approximately 0.00195 square metres, and Senate overlap was zero. These checks do not assert a separate statewide gap/coverage audit against an unavailable reference boundary.

## 6. Imported ACS records

The four supplied Downloads workbooks were copied unchanged to `data/raw/acs/`. SHA-256 comparisons confirm each copy matches its original. Every workbook contains DP02, DP03, DP04 and DP05; geographic labels and estimate/MOE/percent/percent-MOE headings were inspected and validated on every sheet.

| Geography | Geographies | Dashboard statistic records | Numeric estimates | Original profile observations |
| --- | ---: | ---: | ---: | ---: |
| House | 51 | 2,346 | 2,244 | 27,642 |
| Senate | 25 | 1,150 | 1,100 | 13,550 |
| County | 5 | 230 | 220 | 2,710 |
| Hawaiʻi statewide | 1 | 46 | 44 | 542 |
| Total | **82** | **3,772** | **3,608** | **44,444** |

Each original profile observation retains all four measures, raw markers, variable definition, geography label, worksheet/cell references, reference period and workbook checksum. County/state records remain separate comparison geographies. The three imported source records are the two boundary sources and `acs-2024-5yr`.

Imports were rerun successfully; all counts remained unchanged. Existing import commands use stable upserts and transactions rather than creating another ingestion system.

## 7. Supported indicators

There are **46 mapped dashboard indicators**, with **44 numeric reported estimates per geography**. They include population, median age, under-18 and 65+ counts, 65+ share, all 13 published age brackets, median household/per-capita income, all 10 published household-income brackets, poverty rate, households, housing units, tenure, median rent and reported housing-cost-burden counts/universes.

The remaining two mapped fields—poverty population and poverty denominator—are explicitly unavailable because the supplied DP03 profiles do not publish those counts. They were not reconstructed from rounded rates. Thus 164 of the 3,772 records intentionally have no numeric estimate. Raw markers and missing MOEs remain distinct from numeric zero; top-coded values are not treated as exact numbers.

## 8. Geographic and source matching

Every workbook sheet must contain the exact expected geographic set: House 1–51, Senate 1–25, all five county FIPS identifiers, or Hawaiʻi state FIPS 15. Matching uses explicit labels and identifiers, never column order alone. All 76 district profile APIs returned the correct district, 46 mapped records and 44 numeric estimates.

All **3,772 stored mapped records** were reconciled with the original workbook parser, including estimates, MOEs, geography, units, reference period, source cells, raw text and checksums. Independent known-cell tests verify House District 30. Existing plan-compatibility evidence is retained for the 2024 ACS legislative geography labels and 2022 boundary plan.

## 9. House District 30 API

`GET http://localhost:8000/v1/districts/house-30/profile` succeeds and returns these reported values for **2020–2024**:

| Indicator | Estimate | 90% margin of error | Estimate cell |
| --- | ---: | ---: | --- |
| Population | 34,283 | ±1,935 | DP05 DN4 |
| Median household income | $90,180 | ±$9,512 | DP03 DN70 |
| Poverty rate | 9.8% | ±2.6 percentage points | DP03 DP138 |
| Median age | 34.9 years | ±0.8 years | DP05 DN21 |
| Residents aged 65+ | 3,848 | ±442 | DP05 DN27 |
| Residents aged 65+ share | 11.2% | ±1.2 percentage points | DP05 DP27 |
| Median gross rent | $2,481 | ±$233 | DP04 DN152 |

The API serves original workbooks through fixed allowlisted source-download routes. Real workbook download and point-in-polygon lookup were tested.

## 10. Dashboard and charts

Browser testing against the running production frontend confirmed:

- Official imported PostGIS polygons render through the existing ArcGIS Maps SDK; House District 30 is visibly highlighted.
- An actual polygon click selected House District 32, changing the selector, highlight, cards and charts to that district's imported values.
- Switching to Senate selected District 15 and displayed its real profile, including population 83,609 ±2,653 and median household income $92,806 ±$3,772.
- Age and income charts use the workbooks' original bracket definitions, with readable horizontal labels. Housing tenure and reported rent-burden charts render imported counts.
- The all-indicator table exposes 46 records, explicit unavailable values, MOEs and source actions.
- Source dialogs display the original workbook, worksheet/cell, original reported value, reference period, MOE and download link. Escape closes the dialog and restores focus.
- The poverty choropleth and legend update correctly. Renderer and legend use the same tested class-break helper and appropriate units/missing-data color.

Screenshots: [House 30 cards](local-dashboard.png) and [House 30 workbook provenance](local-source-details.png). These are observed browser checks, not a claim that every district was individually clicked or that a full accessibility certification was completed.

## 11. County and state comparisons

House 30 resolves to Honolulu (`county-15003`); statewide comparisons resolve to `state-15`. The Senate 15 comparison page retained its selected chamber/district in the URL and displayed poverty **8.6% ±1.3 pp**, compared with **Honolulu 9.2% ±0.4 pp** and **Hawaiʻi statewide 10.0% ±0.3 pp**. County/state APIs and the browser controls were tested.

`OAHU` maps explicitly to Honolulu. For the district layer's `MAUI` region, Maui and Kalawao are separate contextual benchmarks with the rule disclosed in the API and interface. No exact county intersection or resident allocation is asserted without a supplied county relationship layer. County statistics are never combined or assigned to district residents. See [the methodology](local-data-methodology.md).

## 12. Tests and checks

| Check | Observed result |
| --- | --- |
| Backend unit tests | **76 passed** |
| Actual PostgreSQL/PostGIS integration tests, including seeded data | **4 passed** |
| Frontend tests | **9 passed** |
| Total automated tests | **89 passed** |
| Ruff | Passed |
| Frontend lint / TypeScript (`tsc --noEmit`) | Passed |
| Next.js production build and Python compilation | Passed |
| Geography and statistics validation commands | Passed |
| Final HTTP health / readiness / frontend checks | All 200 |
| Final Docker container check | Running, healthy |

The seeded suite tests every district API, all mapped database values/MOEs/provenance, real county/state comparisons, choropleth values, original workbook delivery and spatial lookup. Existing backend safety/discovery and frontend tests remain included. A dependency deprecation warning was non-failing.

Reproduce the automated checks from the project root:

```bash
make test
RUN_SEEDED_TESTS=1 make test-integration
make lint
make build
make validate-geography validate-statistics
```

## 13. Remaining limits

There is **no current blocker to the verified core local workflow**. Unpublished poverty counts remain unavailable, and Maui/Kalawao comparisons use the documented regional-context rule. Public Esri SDK/basemap resources still require connectivity; this is not a completely offline map package.

Optional Geoportal discovery, DBEDT ingestion, crosswalking and OpenAI assistance remain in the project. No extra dataset or live model call was needed or verified for this core run. Full Compose application containers were not tested; native FastAPI/Next.js plus the Compose database were tested. Keep the current ignored `.env` and persistent volume so existing credentials and data remain consistent.

## 14. Restart commands

The application is already running. For a later restart, stop the previous API/web terminal processes before starting replacements. Keep Docker Desktop running.

From the project root:

```bash
cd /Users/gianvelasco/Desktop/HAIC26
docker compose up -d db
make migrate
```

In terminal 1:

```bash
cd /Users/gianvelasco/Desktop/HAIC26
make dev-api
```

In terminal 2:

```bash
cd /Users/gianvelasco/Desktop/HAIC26
make dev-web
```

Open **http://localhost:3000**. The data is already imported; `make seed` is only needed when intentionally repeating the local import. No API keys or additional downloads are required for that import.

For the production frontend process used during verification, use this instead of `make dev-web`:

```bash
cd /Users/gianvelasco/Desktop/HAIC26
make build
cd apps/web
node node_modules/next/dist/bin/next start --hostname 127.0.0.1 --port 3000
```

Do not delete `haic26_pgdata` or run `docker compose down -v` to restart. Machine-readable SQL/health results are in [local-verification.json](local-verification.json); setup details are in [setup.md](setup.md).
