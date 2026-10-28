# Geoportal access verified during implementation

The actual API definition was downloaded from [the official OpenAPI endpoint](https://geoportal.hawaii.gov/api/search/definition/?f=json) and retained in `data/fixtures/geoportal-openapi.json`. The supplied `/api/search/v1` URL is the API root, not a guessed search operation.

Implemented search route:

```text
GET https://geoportal.hawaii.gov/api/search/v1/collections/dataset/items
q=state house districts
limit=8
startindex=1
```

The definition documents a general text `q`, a maximum limit of 100, and a one-based `startindex`. Actual responses are GeoJSON FeatureCollections with `features`, `numberMatched` and `numberReturned`. Pagination advances by returned records, stops at the documented total, deduplicates canonical service URLs, and has a ten-page ceiling.

DCAT: [official catalog](https://geoportal.hawaii.gov/api/feed/dcat-us/1.1.json). The captured catalog contains 417 records. Records normalize into a Pydantic dataset schema. Raw records, dates, publisher, license and source links are preserved. Search/DCAT duplicates share a deterministic service-derived identity. Catalog metadata modification time is never converted into a demographic reference year.

Fallback order is live Search → live/fresh cached DCAT → a labelled previous DCAT snapshot. With no live service or snapshot, the API returns 503. DCAT files retain retrieval timestamps and source URLs. Cached metadata expires; stale records require fresh underlying service checks before ingestion.

ArcGIS inspection reads the numbered layer metadata using `f=json`, runs the count query, and fetches actual district identifiers. Layer names, field schema, declared plan year, spatial reference, query capability, count and exact number set are checked separately from title similarity. Metadata alone cannot establish statistical variable availability.

Requests use exact hostname allowlists, HTTPS, no redirects, bounded decompressed response sizes, connection/read timeouts and limited retry backoff. Metadata descriptions are converted to text before rendering. Full catalog crawl and arbitrary file fetching are not available to the model.
