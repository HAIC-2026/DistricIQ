# Evidence rubric v1.0.0

Scores are computed by Python and recorded with the evidence used for every category. A high numeric score never overrides a rejection or missing evidence.

| Criterion | Deterministic points |
| --- | --- |
| Authority (25) | 25 for a verified state geodata service with actual source credits; 10 for that official hostname without credits; otherwise 0 |
| Geography (20) | 20 when the inspected service name verifies the requested House/Senate chamber; 10 for an explicitly requested, matching geographic level with inspected service; otherwise 0 |
| Vintage (15) | 15 only when the service description's explicitly recorded boundary plan matches the requested vintage; otherwise 0 |
| Schema (15) | 15 only with an inspected district/GEOID field and every explicitly required field; otherwise 0 |
| Completeness (10) | 10 only when expected chamber count, actual count and unique queried identifier count agree; the validator also checks the exact 1–51 or 1–25 set |
| Access (10) | 5 for public catalog access plus inspected service; 5 for an explicit public-domain license declaration |
| Methodology (5) | 5 for a documented reapportionment commission adoption in actual layer metadata |

Validators reject the wrong chamber/level, known incompatible boundary vintage, known non-public access, explicit prohibited use, missing required inspected fields, invalid layer schema, outside-Hawaiʻi extent and incomplete district coverage. Temporary service failure or absent licensing/vintage evidence is marked insufficient evidence and cannot be recommended. Unknown geographic levels earn no compatibility points.

The first valid candidate by descending score and deterministic dataset ID becomes recommended. Other valid candidates, insufficient-evidence records and rejected records remain distinguishable. Recommendation does not equal ingestion approval.

Known scope: the current rubric is strongest for Hawaiʻi legislative boundary selection. General housing/tract searches expose metadata and limitations, but do not claim a fully generic statistical-source suitability model. Statistical queries explicitly separate the recommended mapping geometry from the ACS source that still needs variable/geography validation.
