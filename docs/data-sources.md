> Historical source-discovery notes. The current database also includes five verified ACS Detailed Tables and a dated program directory. See the [current source inventory](../README.md#data-sources-and-reproducibility) and [research expansion report](research-expansion-report.md). Statements below about unverified live ingestion describe the earlier session.

# Current core source scope

The current database contains only the two official legislative boundary sources and the four supplied ACS workbooks under one ACS source registry entry. See [local data methodology](local-data-methodology.md) for the active sources and ingestion. The references below describe the earlier optional discovery foundation; the DBEDT dataset is not part of the current production database.

# Verified sources and roles

| Source | Role | Reference/vintage and caveats |
| --- | --- | --- |
| [House MapServer/33](https://geodata.hawaii.gov/arcgis/rest/services/AdminBnd/MapServer/33) | Official 2022 House geometry | 51 actual unique districts; identifier `house_id`; query verified; EPSG 3750 service metadata |
| [Senate MapServer/34](https://geodata.hawaii.gov/arcgis/rest/services/AdminBnd/MapServer/34) | Official 2022 Senate geometry | 25 actual unique districts; identifier `senate_id`; query verified |
| [Hawaiʻi Geoportal](https://geoportal.hawaii.gov/) | Metadata discovery | Search and DCAT verified live; catalog records are not proof of every attribute |
| [2024 ACS detailed tables](https://api.census.gov/data/2024/acs/acs5.html) | District, county and statewide statistics | Five-year period 2020–2024. Live district ingestion not verified here because Census API timed out |
| [DBEDT 2024 Data Book section 1 workbook](https://files.hawaii.gov/dbedt/economic/archive/databook/db2024/section01.xls) | Selected contextual population indicator, table 1.06 | July 1, 2024 annual estimates; Maui includes Kalawao; not a district or ACS estimate |

DBEDT's workbook link was obtained from its [official Data Book archive](https://dbedt.hawaii.gov/economic/databook/databook-archive/). The older `db2024` landing page returned 404; the archive provided the working distribution. The actual binary XLS signature, sheet title, column headers, date row, county footnote and statewide conservation were checked. The parser keeps the combined geography instead of pretending that the value represents Maui County alone.

The direct ACS mappings cover population, median age, median household income, per-capita income, poverty numerator and denominator, occupied households, ownership/rental tenure, median gross rent, four age groups and sixteen income brackets. Unsupported cost-burden indicators remain unavailable.

All geography raw captures and approved metadata include official provenance. The checked-in catalog snapshot contains public source descriptions and terms; those terms remain with the data. No resident-level or confidential data was obtained.
