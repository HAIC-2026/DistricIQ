# Geographic methodology

The current boundary plan is the 2022 Hawaiʻi reapportionment. Public ArcGIS layers are convenient rendering sources. Backend analytical geometry must be ingested into PostGIS through the approved CLI; a successful map render does not imply database readiness.

The service metadata declares UTM/NAD83 HARN (latest WKID 3750). Imports explicitly request `outSR=4326`, retain the raw GeoJSON and checksum, validate nonempty Polygon/MultiPolygon topology and Hawaiʻi bounds, check exact district identifiers and normalize Polygon to MultiPolygon. No automatic `buffer(0)` or unrecorded geometry repair is used.

A GiST index supports spatial lookup. `ST_Covers` includes points on polygon boundaries, so point lookup may return more than one district in the same chamber at an exact shared border; callers should report that ambiguity rather than invent a unique assignment.

The frontend uses public ArcGIS layers, local polygon highlighting, a district-list alternative and a basemap source with attribution. Choropleths join only imported statistics whose boundary vintage matches the stored district and whose reference period is 2020–2024. Missing values retain an unavailable state.

Plan compatibility: [Census's 2024 geography-change documentation](https://www.census.gov/programs-surveys/acs/technical-documentation/table-and-geography-changes/2024/geography-changes.html) identifies changed state plans; Hawaiʻi is not listed and falls under the documented unchanged-plan statement. This supports identifier-level 2022/2024 plan matching; it is not a claim of identical vertices across publishers. The compatibility review is retained in `data/manifests/acs-compatibility.json`.

County context currently follows the official district layer's county attribute. Maui/Kalawao are handled conservatively as separate ACS contexts with an explicitly combined DBEDT group. This is contextual membership, not a census-block population crosswalk or a claim that every selected county intersects every district. Exact multi-county intersections would require an independently verified county layer/relationship ingestion and remain a future refinement.
