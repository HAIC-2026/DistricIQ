# Local boundary and ACS profile integration

The core uses only the existing official House/Senate GeoJSON captures and the four supplied ACS workbooks. It does not call Census, OpenAI, DBEDT or Geoportal discovery while importing or displaying these statistics. The ArcGIS SDK renders imported PostGIS geometry through `/v1/geography/districts`; its contextual basemap may request public Esri tiles.

The four original files are retained byte-for-byte in `data/raw/acs`. DP02, DP03, DP04 and DP05 each have a geography label followed by estimate, margin of error, percent and percent margin of error. The workbook geography labels explicitly identify the 2024 legislative geographies. The existing reviewed Census compatibility manifest documents Hawaiʻi's unchanged 2022/2024 district plan; geometry remains labelled the official 2022 plan.

## Geographic identifiers

House and Senate labels must match `State House District N (2024); Hawaii` or the corresponding Senate label. Every sheet must expose exactly the expected 1–51 or 1–25 district set. County names map explicitly to county FIPS 15001, 15003, 15005, 15007 and 15009; Hawaiʻi statewide is state 15. No approximate name matching or numeric-column-order assumption is used.

The official GeoJSON captures contain WGS84 coordinates and `house_id`/`senate_id` identifiers. Polygon topology, Hawaiʻi bounds, exact count and uniqueness are validated before an atomic upsert. Source registry metadata keeps the official service URL, prior inspected service CRS (EPSG 3750), 2022 plan, imported WGS84 CRS, original identifier field, local path and capture checksum.

## Workbooks and uncertainty

All 542 published rows per geography are stored in `acs_profile_observations`: 44,444 original rows across 82 geographies. Their four reported measures, raw strings, sheet/row/column references, geography labels and workbook SHA-256 hashes are retained. The source worksheets do not expose Census API variable codes, so the importer records honest worksheet/cell identifiers rather than inventing detailed-table variable IDs.

Forty-six mapped indicator records per geography feed the existing `statistics` table and dashboard. Forty-four have reported numeric estimates in all 82 geographies. The two explicit unavailable indicators are poverty population and poverty denominator: DP03 supplies a published poverty percentage, but `(X)` or no published value for those counts. Neither is reconstructed by multiplying rounded rates and population.

Reported percentages and percentage MOEs are used directly. `±` and thousands separators are parsed without changing values. `(X)`, `N`, dashes, stars and other nonnumeric markers remain null with their original text preserved. A top-coded `4,000+` value remains a bounded reported string, not a false exact number. Zero remains a numeric zero. Missing MOE is never replaced with zero. MOEs are 90% ACS margins; percentage MOEs are displayed as percentage points.

The reference period is 2020–2024, as identified by the supplied 2024 ACS five-year files and user-provided source description. No single-year interpretation is applied. The original files are available through a fixed allowlisted source-workbook endpoint.

The age chart uses the 13 published DP05 brackets. The income chart uses the 10 published DP03 household-income brackets. Neither is forced into the older detailed-table brackets. All source labels are checked before parsing mapped cells; a changed layout/definition causes an explicit failure. Housing cost burden retains the directly published count brackets and their published universe, without calculating an unsupported combined percentage.

## County comparison rule

The provided district layer has a county/island attribute. `OAHU` maps to Honolulu County, `HAWAII` to Hawaiʻi County and `KAUAI` to Kauaʻi County. `MAUI` identifies the Maui region but does not distinguish Kalawao. For these districts the API presents Maui and Kalawao as **separate contextual benchmarks**, and documents this rule in the response. It never adds the counties, averages their medians or assigns their statistics to district residents.

Without a supplied county boundary/relationship dataset, this implementation does not claim exact county-intersection membership for every Maui-region district. Showing both published geographies with that disclosure supports useful comparison without requiring an additional download or asserting an arbitrary exact county assignment.

## Idempotency and optional sources

Both local imports upsert stable identifiers inside transactions. Re-import verification left 76 district records, 3,772 dashboard statistic records and 44,444 original profile observations, with no duplicate rows. `make seed` requires only local geography and ACS. The earlier live Census importer is retained behind `--live`; existing Geoportal, DBEDT and crosswalk commands remain optional and are not called by the core workflow. The existing optional DBEDT test fixture is historical repository test data, not an asserted user-provided production dataset; no DBEDT source was imported into this database.
