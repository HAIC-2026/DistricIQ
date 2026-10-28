# API v1

Interactive schemas are served at `/docs`; machine-readable specification is at `/openapi.json`.

| Method | Endpoint | Result |
| --- | --- | --- |
| GET | `/healthz` | Process availability and boolean AI configuration; no credentials |
| GET | `/readyz` | Database, PostGIS and migration readiness; 503 until ready |
| GET | `/v1/discovery/search?q=...&limit=8` | Normalized, inspected and scored discovery report |
| GET | `/v1/discovery/datasets/{dataset_id}` | Known catalog record enriched with service metadata |
| POST | `/v1/discovery/evaluate` | `{dataset_ids, purpose}` deterministic evaluations |
| POST | `/v1/discovery/recommend` | `{query, limit, purpose?, use_ai}` bounded discovery and optional AI evidence selection |
| POST | `/v1/discovery/ingestion-plan` | `{dataset_id, purpose}` non-executable plan |
| GET | `/v1/discovery/evaluations` | Last 20 local metadata audit reports; store explicitly identified |
| GET | `/v1/districts?chamber=house` | Imported district records |
| GET | `/v1/districts/{district_id}` | District metadata (`house-30`, `senate-15`, etc.) |
| GET | `/v1/districts/{district_id}/geometry` | GeoJSON from PostGIS |
| GET | `/v1/districts/{district_id}/profile` | District plus source-backed statistics |
| GET | `/v1/districts/{district_id}/demographics` | Profile alias |
| GET | `/v1/districts/{district_id}/indicators/{indicator_code}` | One available indicator or 404 |
| GET | `/v1/indicators` | Documented ACS variable mappings |
| GET | `/v1/districts/{district_id}/compare/county` | Contextual counties with original geography retained |
| GET | `/v1/districts/{district_id}/compare/state` | State benchmark alongside district |
| GET | `/v1/geography/point-lookup?lon=...&lat=...` | Every polygon covering the point |
| GET | `/v1/geography/bounds` | Stored geometry bounds |
| GET | `/v1/geography/layers` | Reviewed source manifest |
| GET | `/v1/geography/choropleth?indicator=population&chamber=house` | Compatible verified values only |
| GET | `/v1/sources` | Imported source registry |
| GET | `/v1/sources/{source_id}` | Imported provenance record |
| GET | `/v1/statistics/{statistic_id}/provenance` | Statistical method, original variables and available MOE |

Query/body validation failures return 422. Discovery throttling returns 429; oversized POST requests return 413; known-record misses return 404. External-source and database outages return 503 with structured `{error:{code,message}}`. Readiness has a distinct structured status response. No exception body exposes a database URL or private key.

Example:

```bash
curl -X POST http://localhost:8000/v1/discovery/recommend \
  -H 'Content-Type: application/json' \
  -d '{"query":"Find the best official Hawaii State House district boundaries","limit":8,"use_ai":false}'
```

There is no approval, ingestion execution or arbitrary-URL endpoint. IDs refer only to known catalog records, not user-supplied remote resources.

Current local-data additions: `GET /v1/geography/districts?chamber=house|senate` returns imported PostGIS geometry as a GeoJSON FeatureCollection. `GET /v1/sources/acs-2024-5yr/workbooks/{house|senate|county|state}` downloads the fixed original source workbook. No arbitrary path or URL is accepted. Profiles include reported labels, display groups/order and exact workbook provenance.
# Conversational assistant

`GET /v1/assistant/status` returns the configured flag, model name and reference period without credentials.

`POST /v1/assistant/chat` accepts `{message, district_id, history}`. `district_id` is a canonical ID such as `house-30` or null. History is a bounded list of complete user/assistant pairs. The response contains the server-rendered `message`, retrieved `citations`, calculated `comparisons`, updated `district_id`, `tools_used`, `warnings` and `reference_period`.

Chat has a 20,000-byte body limit, a 2,000-character message limit, bounded history, a 65-second overall deadline, two concurrent requests and ten requests/minute per client per API process. Invalid requests return 422, unavailable configuration 503, failed/ungrounded model output 502 and capacity/rate limits 429. No-store response headers apply. See [the Phase 2 report](phase2-assistant-report.md) for the registered read-only tools and source-grounding method.
