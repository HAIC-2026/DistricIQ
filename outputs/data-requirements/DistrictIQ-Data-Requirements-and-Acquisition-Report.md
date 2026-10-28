# DistrictIQ Hawaiʻi — Data Requirements & Acquisition Report

**Research and database audit date: October 26, 2026, Hawaiʻi time.**

**Recommendation:** expand safe access to the ACS observations already in PostgreSQL first, then acquire a small set of directly published legislative-district cross-tabulations. Keep program information in a separately verified, versioned directory. Neither tract allocation nor RAG is a prerequisite for this expansion.

Companion documents: [complete existing-data inventory](existing-data-inventory.md), [standalone30-question matrix](question-to-data-matrix.md), [dataset catalog](dataset-catalog.md), and [program information catalog](program-information-catalog.md). JSON versions accompany the matrix and catalogs in the same directory.

This study inspected the existing repository, live PostgreSQL data, source registry, migrations, ingestion code and assistant tools. It researched official metadata and agency publications. It did **not** change application code, schema, credentials, imported observations or running services; no migrations or new statistical imports were performed. Only research artifacts and bounded metadata/audit files were written. Published web documents were inspected for research, without mass-downloading datasets into the project.

**Verification boundary:** table identities and product geography documentation were checked, but every cell for all 76 districts has not been downloaded or validated. Sample Census data queries without a Census key returned redirects or timed out. Metadata availability is not a claim of successful data acquisition. Some current program documents were inaccessible, and their unverified rules are identified below.

## A. Existing Data Inventory

### A1. What is actually in PostgreSQL

| Imported asset | Audited contents | Interpretation |
| --- | --- | --- |
| House boundaries | 51 distinct House districts, 2022 vintage | Existing official polygons; keep them |
| Senate boundaries | 25 distinct Senate districts, 2022 vintage | Existing official polygons; keep them |
| Comparison geographies | 5 counties and Hawaiʻi statewide, in the ACS statistical records | Includes Kalawao separately; statistical records do not imply county geometries are imported |
| Mapped statistics | 3,772 rows across 82 geographies; 46 field definitions | 3,608 numeric estimates; 164 intentional null estimates |
| Original ACS profile observations | 44,444 rows across 82 geographies | 542 distinct worksheet row definitions per geography; 42,792 numeric estimate cells, with percentages/MOEs separately preserved |
| DP02 | 154 row definitions × 82 = 12,628 observations | Household composition, social characteristics and access indicators |
| DP03 | 137 × 82 = 11,234 | Employment, income sources, insurance and poverty rates |
| DP04 | 143 × 82 = 11,726 | Housing characteristics, tenure and housing costs |
| DP05 | 108 × 82 = 8,856 | Population, age, sex, race/ethnicity and other demographics |
| Approved imported sources | Exactly three source records | `house-boundaries-2022`, `senate-boundaries-2022`, `acs-2024-5yr` |
| Database structure | Alembic revision `0002`; PostGIS 3.5.2 recorded by audit | This study makes no migration changes |

Mapped row counts by geography are 2,346 House, 1,150 Senate, 230 county and 46 statewide. Every geography has 44 numeric mapped estimates and the same two unavailable fields: `poverty_population` and `poverty_denominator`. Their absence is deliberate: the supplied DP03 poverty section reports percentages but not those counts/universes.

The four unchanged official workbooks are already under `data/raw/acs/`:

- `acs2024_5yr_house_hi.xlsx`
- `acs2024_5yr_senate_hi.xlsx`
- `acs2024_5yr_counties_hi.xlsx`
- `acs2024_5yr_state_hi.xlsx`

The original district GeoJSON files are under `data/raw/geography/`. The live state boundary services remain [House layer 33](https://geodata.hawaii.gov/arcgis/rest/services/AdminBnd/MapServer/33) and [Senate layer 34](https://geodata.hawaii.gov/arcgis/rest/services/AdminBnd/MapServer/34). PostgreSQL stores district multipolygons in EPSG:4326; official services use Hawaiʻi’s projected CRS, EPSG:3750. Preserve the source CRS separately from the storage CRS.

No additional DBEDT economic data, tract/block-group observations, population relationship files, administrative participation datasets or program eligibility directory were verified as imported. A DBEDT manifest/discovery candidate is not evidence of a populated production dataset. Do not import it just because a manifest exists.

A final read-only PostgreSQL transaction after report drafting reconfirmed **76 district rows, 3,772 mapped statistic rows, 44,444 original observation rows and 3 source rows**. No research-stage data import changed these counts.

### A2. Mapped statistics versus preserved observations

The assistant’s current mapped set covers population, median age, under-18 count, 65+ count/share, median household and per-capita income, poverty rate, household and housing-unit totals, owner/renter household counts, median gross rent, 13 age bins, 10 income bins, and selected housing-burden cells/denominators. Two registered poverty count fields are unavailable. The complete 46-field list and all 542 row definitions are in **`existing-data-inventory.md`** alongside this report.

Additional useful data already preserved, but outside the chatbot’s current allowlist, includes:

| Topic | Existing workbook evidence | What it enables without a new download |
| --- | --- | --- |
| Older adults living alone | DP02 rows 12 and 16 | Sum two disjoint counts, with a derived MOE |
| Households with children | DP02 row 17 | Report count/share of households with at least one resident under 18 |
| Grandparents responsible | DP02 row 52 | Report responsible-grandparent people; row 58 repeats the same total |
| Education | DP02 rows 69–78 | Age-25+ attainment, including published BA+ total/share |
| Disability | DP02 rows 83–90 | Civilian noninstitutionalized disability, including broad age subgroups |
| Social Security, retirement, SSI, cash assistance and SNAP | DP03 rows 74–82 | Separate household receipt measures, not primary-income dependence or individual enrollment |
| Child and older-adult poverty | DP03 rows 139 and 145 | Published rates/MOEs; not subgroup poverty counts |
| Insurance and employment | DP03 relevant sections | Resident insurance/labor-force context, using each row’s own universe |
| Vehicles, crowding, housing age, value and costs | DP04 relevant sections | Service-access and housing-needs context |
| Language, migration, marital status, enrollment, veteran status and ancestry | DP02 relevant sections | Broader resident-profile questions after metadata curation |
| Computer and broadband subscription | DP02 rows 173–174 | Household digital-access barriers; subscription is not network availability/speed |
| Sex and race/ethnicity | DP05 sections | Published demographic categories; race and Hispanic origin overlap |

These 542 rows are **not 542 independent indicators**, and every numeric percent-column cell is not a percentage. Some total rows repeat their count in that column. Definitions such as “With a disability,” “Under 18 years” and “Median (dollars)” require parent section/universe context. Row numbers are worksheet references, not Census API variable IDs. Preserve that distinction when expanding retrieval.

For a concrete database-backed audit example, House District 30’s original rows contain:

| Observation | Audited value | Meaning |
| --- | --- | --- |
| DP03 row 74 | 2,043 ±215 households | Any Social Security receipt, all household ages |
| DP03 row 82 | 1,660 ±293 households; 19.3% ±3.2 percentage points | Reported SNAP receipt in the past 12 months |
| DP02 row 78 | 24.6% ±2.2 percentage points | Bachelor’s degree or higher, population 25+ |
| DP03 row 145 | 13.6% ±4.5 percentage points | Poverty among people 65+ in the poverty universe; count unavailable |
| DP02 rows 12 and 16 | 102 ±57 and 265 ±95 | Male and female older householders living alone; combined estimate 367 is calculated, not a separately published total |

All are 2020–2024 ACS estimates, not 2026 point-in-time counts. Source workbook hashes, sheet/cell references, reported strings and geography labels are retained in the audit/database. No values in this report are newly invented or hardcoded into the application.

### A3. Current retrieval bottleneck

Inspected implementation locations:

- `services/api/app/models/entities.py`: `Source`, `District`, `Statistic`, `ACSProfileObservation`, `CrosswalkWeight`, `EvaluationRecord`.
- `services/api/alembic/versions/0001_foundation.py` and `0002_acs_profile_observations.py`.
- `pipelines/census/workbooks.py` and `pipelines/census/ingest.py`: existing import paths.
- `services/api/app/analytics/acs_profiles.py`: 46 dashboard aliases and worksheet mappings.
- `services/api/app/ai/district_tools.py` and `district_assistant.py`: constrained tool schemas, evidence and answer rendering.
- `services/api/app/services/district_service.py` and `comparison_service.py`: existing statistical/benchmark services.
- `data/manifests/` and the `sources` table: discovery versus imported-source distinction.

The eight read-only data tools are `get_district_profile`, `get_district_indicators`, `compare_districts`, `compare_benchmark`, `get_distribution`, `get_housing_statistics`, `get_statistic_sources`, and `explain_available_indicators`. `present_answer` finalizes server-rendered facts. The profile tool returns six summary fields; the indicator enum derives from the fixed 46-field registry. Evidence retrieval filters the current source and period. It does **not** search `ACSProfileObservation`.

Therefore, “in PostgreSQL” does not mean “currently answerable by the chatbot.” Retain the existing evidence/citation safeguards while adding metadata-driven access to approved raw measures. A blanket rejection of all age-by-income questions should eventually become a capability check: some published detailed tables provide genuine cross-tabulations.

## B. Question-to-Data Matrix

The table includes each question’s universe, existing raw versus mapped availability, new source, geographic suitability and answerability. Source table links are in section C. A standalone matrix and machine-readable version accompany this report.

Legend: **0 reuse** means no new statistical download; retrieval or controlled calculation work may still be required. **1/2/3** correspond to the report’s acquisition priorities. “Available” distinguishes mapped chatbot fields from preserved raw rows. Official source URLs for table IDs appear in the report catalog and dataset-catalog.json. ACS recommendations use the 2020–2024 five-year release.

| Question | Required indicators and universe | Already available? | Additional source | Geographic availability | Answerability | Priority |
| --- | --- | --- | --- | --- | --- | --- |
| 1. How many kūpuna in my district rely on Social Security as their primary income? | People 65+; define individual versus household income and “primary” (e.g. >50%) before measurement. Joint age × Social Security receipt × share of total income. | No exact count. Raw DP03 rows 74–77 report all-household Social Security/retirement receipt and recipient-household means. | S0103 adds households with older householders receiving Social Security; B19037 adds older-householder income. Neither measures primary dependence. PUMS only for a separately defined state/PUMA study. | Receipt proxy: direct SLD. Primary-dependence custom estimate: state/PUMA only. | Exact district answer unsupported; offer clearly labeled receipt proxy, not dependence. | 1 proxy / 3 custom |
| 2. What percentage of residents in my district are 65 or older? | All residents. Age 65+ share and MOE. | Mapped older_adult_share; raw DP05 row 27 percentage. | None. | Direct House/Senate, county and state. | Reported estimate available now. | 0 reuse |
| 3. How many kūpuna in my district live below the poverty line? | People 65+ for whom poverty status is determined. Age 65+ below-poverty count and matched denominator. | Raw DP03 row 145 has 65+ poverty rate/MOE, but its count is (X). | B17001; S0103 as a complementary profile. | Direct SLD/county/state. | Count is a documented sum of disjoint age/sex poverty cells after import; existing rate can be exposed now. | 1 |
| 4. Are older residents in my district more likely to rent or own their homes? | Literal: people 65+ in occupied housing. Available alternative: households with householder 65+. Age × tenure with person or household universe made explicit. | No age × tenure cross-tab in current profiles. | B25007; B25011 for older people living alone by tenure. | Direct SLD for older-householder household measure. | Answer reworded household measure after import; literal all-older-residents measure not established by these tables. | 1 |
| 5. How does the kūpuna population in my district compare with the statewide average? | All residents, identifying age cutoff 65+. Age 65+ count/share for district and state. | Mapped age_65_plus and older_adult_share in both geographies. | None. | Direct SLD/state. | Reported estimates and calculated percentage-point difference available. | 0 reuse |
| 6. How many older adults live alone in my district? | People 65+ living in one-person households; excludes group quarters. Older male-alone + older female-alone counts. | Raw DP02 rows 12 and 16, each with MOE; not in chatbot allowlist. | None for total; B09021 for richer arrangements or B25011 for tenure. | Direct SLD/county/state. | Derived disjoint-cell sum using existing data; expose controlled formula/MOE. | 0 reuse |
| 7. How many families in my district struggle to afford basic necessities? | Families of a defined composition; hardship needs an operational definition. Family composition-specific budget threshold jointly with comparable disposable/gross income and costs. | Poverty rates, income bands and housing burden are available proxies; no direct hardship count. | DBEDT 2024 Self-Sufficiency Income Standard; B19037/B17024 give limited additional context. | Budget: county/state, not SLD. Income/poverty proxies: direct SLD. | Can report measured proxies and county budget scenarios; exact family hardship count unsupported. | 2 |
| 8. What percentage of households spend more than 30% of their income on housing? | Occupied households with computable housing-cost share, split renter, owner with mortgage, owner without mortgage. 30–34.9 and 35%+ cells plus each computed-universe denominator. | DP04 raw rows 127/131/132,134/140/141,155/160/161. Most counts mapped; unmortgaged denominator only raw. | None for ≥30% computed-universe estimate; B25106 adds income cross-tabs. | Direct SLD/county/state. | Derived weighted count/denominator ratio after raw retrieval; not average of three percentages. | 0 reuse |
| 9. How many households in my district earn less than $50,000 annually? | Households; annual household income in 2024 inflation-adjusted dollars. Sum the five income bins below $50,000. | Mapped income_profile_01–05 / DP03 rows 60–64. | None; B19037 only if age subgroup requested. | Direct SLD/county/state. | Derived sum available from existing records; current tool returns brackets, not a guaranteed summed fact. | 0 reuse |
| 10. Are residents in my district experiencing higher poverty rates than neighboring districts? | People with poverty status determined, same chamber/period; define spatial neighbor. Poverty rates/MOEs plus shared-boundary adjacency from existing polygons. | Mapped poverty_rate for all districts; existing PostGIS geometry sufficient for adjacency. | None for rates; B17001 adds actual poverty counts/denominators. | Direct SLD, same chamber. | Descriptive comparison now for named districts; spatial-neighbor tool and significance method still needed. | 0 reuse |
| 11. How does median household income compare with median rent in my district? | All households for income; renter-occupied units paying cash rent for median gross rent. Annual median household income and monthly median gross rent. | Both mapped, with MOEs. | None. | Direct SLD/county/state. | Display both now; optional annualized rent/income benchmark as a clearly labeled ratio of separate medians. | 0 reuse |
| 12. How many households rely on government assistance as a source of income? | Households; define specific benefit and whether receipt or dependence is intended. SSI, cash public assistance, SNAP and possibly a published union; primary-income share would be separate. | Raw DP03 78/80/82 gives separate SSI/cash/SNAP receipt counts, not reliance or union. | B19058 provides cash assistance OR SNAP; S2201 receipt subgroups. | Direct SLD/county/state for survey receipt; administrative district counts not verified. | Program-specific receipt answer via raw data; defined union after import; all-assistance dependence count unsupported. | 0 reuse / 1 union |
| 13. How many renters in my district are considered severely cost-burdened? | Cash-rent renter-occupied housing units/households with computable share; not individual renters. Published 50%+ gross-rent/income cell and MOE. | No. DP04 ends at 35%+; this cannot isolate 50%+. | B25070. | Direct SLD/county/state. | Reported 50%+ bin after import, with universe and not-computed exclusions. | 1 |
| 14. What percentage of residents in my district live in owner-occupied housing? | People in occupied housing units, or all residents if explicitly including group quarters in denominator. Person counts by tenure and appropriate population denominator. | DP04 owner/renter counts and percentages are households, not people. | B25008, with DP05 total population only if all-resident denominator is requested. | Direct SLD/county/state. | Derived person-based share after import. | 1 |
| 15. Are housing costs higher in my district than in the rest of Honolulu County? | Comparable renter/owner housing universes. “Rest” excludes district and differs from whole county. Same cost indicator for district and comparator; remainder medians require microdistribution, not subtraction. | Mapped district and whole-Honolulu medians plus some burden counts. | No download for whole-county comparison; full-county/remainder counts may be constructed only for additive compatible cells and containment. | SLD and whole county directly; county-minus-district median not published in current data. | Whole-county descriptive benchmark available; exact rest-of-county median unavailable. | 0 reuse |
| 16. How many households might be at risk of housing instability? | Households; requires a validated risk definition and observation period. Burden, low income, overcrowding, tenure and possibly arrears/eviction/displacement information. | Several burden, crowding and income proxies in raw DP04/DP03; no instability label or validated risk score. | B25070/B25106; HUD CHAS later for housing problems. Administrative eviction/arrears district series not verified. | Proxy ACS direct SLD; CHAS smaller-area/county; risk outcome coverage unknown. | Report separately measured risk factors; no defensible unique at-risk count by summing overlaps. | 1 proxies / 3 outcome |
| 17. What are the biggest housing-related challenges shown by my district’s demographic data? | Distinct housing/household universes per measure. Rent, burden, tenure, vacancy, crowding and county/state benchmarks, each with MOE. | Mapped rent/tenure/burden plus raw DP04 crowding, housing age, value and costs. | B25070/B25106 deepen analysis; HHFDC inventory supports referrals, not resident outcomes. | Direct SLD for ACS; property points for inventory. | Evidence-based descriptive summary now, with expanded raw retrieval; rank only compatible metrics. | 0 reuse / 1 detail |
| 18. Are there more renters or homeowners in my district? | Clarify households versus people; default tenure of occupied households. Owner/renter occupied household counts. | Mapped owner_occupied and renter_occupied; DP04 54/55. | None for households; B25008 for people. | Direct SLD/county/state. | Reported household estimates now. | 0 reuse |
| 19. How many children under 18 live in my district? | All residents under age 18. Under-18 population. | Mapped age_under_18; raw DP05 row 22. | None. | Direct SLD/county/state. | Reported estimate now. | 0 reuse |
| 20. What percentage of households have children under 18? | Households with one or more people under 18, unless own-child relationship is specifically requested. Published households-with-under 18 percent and MOE. | Raw DP02 row 17, not chatbot allowlist. | None. | Direct SLD/county/state. | Reported percentage once raw retrieval exposed. | 0 reuse |
| 21. How many children live in households below the poverty line? | Children under 18 for whom poverty status is determined; poverty assigned using Census family/unrelated-person rules. Under18 below-poverty count; clarify family-poverty concept rather than generic household-income cutoff. | Raw DP03 row 139 provides child-poverty rate only; count (X). | B17001. | Direct SLD/county/state. | Disjoint age/sex cell sum after import; rate can be exposed now. | 1 |
| 22. What percentage of adults have a bachelor’s degree or higher? | Conventionally population age 25+; “adults”18+ is a different question. Published BA+ percent and MOE for age 25+. | Raw DP02 row 78, denominator row 69; not allowlisted. | None for 25+; an age-specific education table would need separate verification for an18+ request. | Direct SLD/county/state. | Reported25+ estimate once raw retrieval exposed. | 0 reuse |
| 23. How many grandparents are responsible for raising their grandchildren? | Grandparents living with own grandchildren under 18 who report responsibility for basic needs. Responsible-grandparent people and MOE. | Raw DP02 row 52 (row 58 repeats same total in a later section). | None for total; S1002 for subgroup detail. | Direct SLD/county/state. | Reported count once raw retrieval exposed. | 0 reuse |
| 24. How does educational attainment in my district compare with the statewide average? | Population25+ in district and state. Same education category percentages/denominators/MOEs. | Raw DP02 rows69–78 across all 82 geographies. | None. | Direct SLD/state. | Reported estimates and calculated percentage-point differences after raw retrieval. | 0 reuse |
| 25. Which government assistance programs might be relevant to low-income kūpuna in my district? | District older-adult need signals; program eligibility assessed for individuals/assistance units separately. Age, poverty, disability, tenure and program-specific rules/referral geography. | Older share mapped; older poverty/disability/alone and SSI/SS receipt raw. No verified program directory currently imported. | Versioned SSI, AABD, SNAP, Med-QUEST, Medicare Savings/Extra Help, housing, H-HEAP and aging-service official records; B17001/S0103 enrich need. | Need direct SLD; program rules statewide/federal/county service areas; not district eligibility counts. | Explain potential relevance with citations; individual eligibility requires additional inputs and agency determination. | 1 statistics / 2 program directory |
| 26. How many residents might benefit from affordable housing assistance? | People versus households must be resolved; measured housing need ≠ qualifying applicants. Burden/AMI-income/tenure/household-size joint cells plus program rules, capacity and actual participation. | Rent, income and burden proxies only. | B25070/B25106, HUD income limits; HUD CHAS later; HPHA/county participation data if published or supplied. | Direct ACS SLD proxy; HUD county/other areas; district administrative counts not verified. | Quantify specific measured household needs; no exact eligible-person or unmet-service count. | 1 proxies / 2 rules / 3 participation |
| 27. What demographic indicators suggest a need for food assistance programs? | People in poverty, older people/children, and households reporting SNAP; separate universes. Poverty and child/older poverty, low income, disability, SNAP receipt, vehicles and food-access context. | Poverty/income mapped; SNAP, age poverty rates, disability and vehicles raw. | B17001/S2201/B22003; program directory. | ACS direct SLD; administrative participation generally larger reporting areas. | Report indicators and potential relevance, not a measured food-insecurity count. | 0 reuse / 1 cross-tabs |
| 28. Which existing programs support older adults with limited retirement income? | Individuals/assistance units with program-specific ages/resources/Medicare or functional status. Verified purposes, eligibility rules, benefit types and application/referral paths. | No program directory in imported sources. Raw retirement/SSI/SS measures offer district context only. | Official SSI, AABD, SNAP, Med-QUEST, Medicare Savings, Extra Help, aging/nutrition/Kūpuna Care, housing and H-HEAP records. | Rules federal/state; county/local administration and availability. | Program information answer after directory curation, with eligibility caveats. | 2 |
| 29. What information would be needed to estimate how many households might qualify for SNAP? | SNAP assistance units (food purchase/preparation groups), which may differ from ACS households. Current Hawaiʻi gross/net income rules, deductions, resources where applicable, elderly/disability exceptions, assistance-unit composition, status and other current requirements. | ACS income bands, household characteristics, reported SNAP receipt; not complete eligibility inputs or joint distribution. | Current DHS SNAP rules plus S2201/B22003; validated state/PUMA microsimulation only if later justified. | Rules statewide; descriptive SLD cells; eligibility simulation not reliable at SLD from marginals. | Can explain missing inputs; cannot count eligible district households from current aggregates. | 2 rules / 3 simulation |
| 30. What demographic trends could help government agencies plan community services? | Consistent resident/household populations across comparable time periods and boundaries. Age, poverty, disability, income, housing, language and access series with identical definitions/geography. | One imported2020–2024 period: supports needs snapshot, not change over time. | Consistent-vintage prior ACS/Decennial series after boundary review; county/state PEP/LAUS, DOE and service locations for context. | Direct SLD only for compatible plans; county/state trends separately. 2024 Comparison Profiles omit SLD. | Snapshot now; documented trend comparisons later. | 2 context / 3 district history |

## Per-question methodological limitations

**Q1.** Social Security ≠ SSI; receipt ≠ reliance; household benefit total ≠ person count. No multiplication of marginal totals.

**Q2.** Use published percent/MOE; retain total-population universe and 2020–2024 period.

**Q3.** Do not multiply DP05 total 65+ population by the DP03 poverty rate; poverty excludes some residents.

**Q4.** A 65+ householder is not every 65+ resident. Do not relabel household tenure as resident tenure.

**Q5.** Statewide share is not an average district count; district is part of state, so uncertainty is correlated.

**Q6.** Count people/one-person households consistently; do not include institutional residence or infer loneliness.

**Q7.** Family ≠ household; basic-needs budgets ≠ Census poverty. A broad income band cannot determine how many families fall below a composition-specific threshold.

**Q8.** Bins support ≥30%, not strict >30%. Exclude and disclose not-computed cases; use appropriate derived MOE.

**Q9.** Households do not necessarily earn wages; income includes other sources. Propagate MOE; sum estimates, not margins of error.

**Q10.** Numerically consecutive districts need not be neighbors. Rook versus point-touch adjacency must be stated; “higher estimate” does not imply significant difference.

**Q11.** Different universes. 12×median rent / median income is not the median household’s burden or the share of renters cost-burdened.

**Q12.** SNAP is noncash; benefits overlap. Do not add SSI, SNAP and cash counts or infer primary dependence.

**Q13.** Confirm convention: published ≥50% bin cannot identify strict >50%. Explain household versus person count.

**Q14.** Do not use owner-household share or rounded average household size to manufacture exact resident counts; group quarters alter denominator.

**Q15.** Do not subtract medians. District may not be fully within Honolulu; for multi-county districts provide all relevant county contexts, not a fabricated blended county.

**Q16.** Cost burden is not a prediction of eviction/homelessness. Adding overlapping vulnerable groups double-counts households.

**Q17.** No causal diagnosis or resident-level inference. Vacancy categories are not necessarily available housing; unequal denominators cannot be combined into one count.

**Q18.** Call them renter/owner households, not number of property owners or individual renters; a landlord can live elsewhere.

**Q19.** Use exact under-18 total; do not include the entire 15–19 age-distribution bin.

**Q20.** “Children of householder” is narrower than any resident under 18; use the requested definition, not sum of household-type subrows.

**Q21.** Household income and family poverty differ. Do not multiply all children by a mismatched rate denominator.

**Q22.** State age 25+ explicitly. BA+ row already includes graduate degrees; do not double-count by adding both a combined total and component.

**Q23.** Not necessarily sole/legal custody. Do not double-count repeated total; B10002 counts grandchildren, not grandparents.

**Q24.** Compare consistent categories and period; state includes district; differences need appropriate uncertainty handling.

**Q25.** 65+ and60+ program cutoffs differ. Low income alone does not establish assets, functional need, status, household unit or availability.

**Q26.** Do not subtract county participation from district ACS needs. AMI-adjusted limits differ from a fixed $50k threshold; waitlists and eligibility differ.

**Q27.** Poverty and SNAP receipt are not direct food insecurity measures; SNAP nonreceipt is not proof of noneligibility or unmet eligible need.

**Q28.** Retirement income ≠ total countable income; Social Security retirement is not means-tested SSI. Never promise enrollment or benefits.

**Q29.** Do not use a contiguous-U.S. income chart, old effective year, poverty threshold as guideline, or all households under a chosen income band as eligible.

**Q30.** Do not join pre/post2022 district numbers as identical areas. Overlapping five-year estimates are correlated; location of a school is not residence of its pupils.


## C. Recommended Dataset Catalog

### C1. Priorities and acquisition scope

**Priority 1 — essential:** curated access to existing raw observations, followed by targeted 2024 ACS five-year detailed/subject tables directly published for Hawaiʻi’s legislative districts. Start with five tables, validate them, then expand to ten. Do not retrieve a full national ACS extract.

**Priority 2 — high value:** selected subgroup tables where they add new combinations, an official program directory, current housing-program thresholds and affordable-property locations, county/state economic trends and selected facilities. County/state statistics remain labeled context.

**Priority 3 — advanced:** tract/block-group allocation, CHAS-derived district estimates, custom PUMS analysis, health modeling, administrative district participation and historical boundary harmonization. These require a specific decision use case and methodology before acquisition.

For Census catalog entries below, the recommended year is the **2024 five-year release, reference period 2020–2024**, to match existing data. “Direct SLD” means the published product supports upper/lower legislative geographies; each table’s Hawaiʻi records, annotations and MOEs still need acquisition QA. The state’s [2024 geography-change documentation](https://www.census.gov/programs-surveys/acs/technical-documentation/table-and-geography-changes/2024/geography-changes.html) supports compatibility with the 2022 Hawaiʻi plans; it does not prove vertex-for-vertex identity of state and Census polygons.

| Dataset / agency | Exact table or official source | Geography | Years | Format | New capabilities | Priority |
| --- | --- | --- | --- | --- | --- | --- |
| Poverty Status in the Past 12 Months by Sex by Age — U.S. Census Bureau | [B17001](https://api.census.gov/data/2024/acs/acs5/groups/B17001.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | Direct subgroup counts: children and people 65+ below poverty, plus matched poverty universes; closes the two null dashboard poverty fields. | 1 |
| Gross Rent as a Percentage of Household Income in the Past 12 Months — U.S. Census Bureau | [B25070](https://api.census.gov/data/2024/acs/acs5/groups/B25070.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | Separates the 50%+ rent-burden bin missing from DP04; preserves not-computed cases. | 1 |
| Tenure by Age of Householder — U.S. Census Bureau | [B25007](https://api.census.gov/data/2024/acs/acs5/groups/B25007.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | Owner/renter comparisons for households with a householder aged 65+, not all older people. | 1 |
| Tenure by Household Type (Including Living Alone) and Age of Householder — U.S. Census Bureau | [B25011](https://api.census.gov/data/2024/acs/acs5/groups/B25011.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | Genuine joint counts for older householders living alone by tenure; no Social Security dependence dimension. | 1 |
| Age of Householder by Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) — U.S. Census Bureau | [B19037](https://api.census.gov/data/2024/acs/acs5/groups/B19037.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | Income bands for households headed by an older adult; household income is not an individual pension or benefit. | 1 |
| Total Population in Occupied Housing Units by Tenure — U.S. Census Bureau | [B25008](https://api.census.gov/data/2024/acs/acs5/groups/B25008.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | Person-based tenure counts; resolves the difference between residents and households. | 1 |
| Population 65 Years and Over in the United States — U.S. Census Bureau | [S0103](https://api.census.gov/data/2024/acs/acs5/subject/groups/S0103.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | A coherent older-adult profile with income-source receipt for older-householder households; does not measure primary Social Security dependence. | 1 |
| Food Stamps/Supplemental Nutrition Assistance Program (SNAP) — U.S. Census Bureau | [S2201](https://api.census.gov/data/2024/acs/acs5/subject/groups/S2201.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | SNAP receipt cross-tabulations, including households with a person 60+ and selected poverty/household characteristics; not eligibility. | 1 |
| Public Assistance Income or Food Stamps/SNAP in the Past 12 Months for Households — U.S. Census Bureau | [B19058](https://api.census.gov/data/2024/acs/acs5/groups/B19058.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | Reported union of cash public-assistance income or SNAP receipt, avoiding double-counting two overlapping totals; not all government assistance. | 1 |
| Tenure by Housing Costs as a Percentage of Household Income in the Past 12 Months — U.S. Census Bureau | [B25106](https://api.census.gov/data/2024/acs/acs5/groups/B25106.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | Genuine income-bracket × tenure × housing-cost-share cells, beyond separate income and burden totals. | 1 |
| Sex by Age by Disability Status — U.S. Census Bureau | [B18101](https://api.census.gov/data/2024/acs/acs5/groups/B18101.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | Finer age/sex disability comparisons beyond coarse DP02 age bands; excludes institutionalized residents. | 2 |
| Living Arrangements of Adults 18 Years and Over by Age — U.S. Census Bureau | [B09021](https://api.census.gov/data/2024/acs/acs5/groups/B09021.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | Living alone, spouse/partner and other arrangements by adult age; older-alone total already derivable from DP02. | 2 |
| Age by Ratio of Income to Poverty Level in the Past 12 Months — U.S. Census Bureau | [B17024](https://api.census.gov/data/2024/acs/acs5/groups/B17024.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | Age-specific near-poverty ranges; ratios to Census poverty thresholds are not current program eligibility guidelines. | 2 |
| Receipt of Food Stamps/SNAP in the Past 12 Months by Poverty Status in the Past 12 Months for Households — U.S. Census Bureau | [B22003](https://api.census.gov/data/2024/acs/acs5/groups/B22003.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | Poverty × SNAP receipt; cannot identify eligible nonparticipants. | 2 |
| Receipt of Food Stamps/SNAP in the Past 12 Months by Presence of People 60 Years and Over for Households — U.S. Census Bureau | [B22001](https://api.census.gov/data/2024/acs/acs5/groups/B22001.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | Compact alternative to S2201 for the older-presence × SNAP question; acquire instead of duplicate cells when S2201 suffices. | 2 |
| Grandparents — U.S. Census Bureau | [S1002](https://api.census.gov/data/2024/acs/acs5/subject/groups/S1002.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | Caregiver characteristics and poverty/context; responsible-grandparent total already in DP02. | 2 |
| Health Insurance Coverage Status by Sex by Age — U.S. Census Bureau | [B27001](https://api.census.gov/data/2024/acs/acs5/groups/B27001.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | Age/sex uninsured subgroups beyond the overall insurance information already in DP03; insurance is not healthcare access or eligibility. | 2 |
| Household Income in the Last 12 Months (in 2024 Inflation-Adjusted Dollars) by Presence and Type of Internet Subscription in Household — U.S. Census Bureau | [B28004](https://api.census.gov/data/2024/acs/acs5/groups/B28004.html) | 2024 published state legislative upper/lower districts, counties, state; 2022 Hawaiʻi plan compatibility documented. Verify all 76 IDs and each cell on acquisition. | 2020–2024 | Census API JSON or data.census.gov CSV + metadata | Genuine income × internet-subscription cross-tab for low-income digital-access barriers; no broadband speed or network-service availability claim. | 2 |
| Self-Sufficiency Income Standard Estimates for the State of Hawaiʻi and Counties for 2024 — Hawaiʻi DBEDT READ | [DBEDT-SSIS-2024](https://files.hawaii.gov/dbedt/economic/reports/self-sufficiency/self-sufficiency_2024.pdf) | State and four reported county family-budget areas; not legislative districts | 2024 budgets; December 2025 publication | PDF, tables I.A and IV.A–E | A Hawaiʻi-specific basic-needs benchmark by family composition; cannot count district families below it from marginal income totals. | 2 |
| FY 2026 Income Limits — HUD | [HUD-IL-2026](https://www.huduser.gov/portal/datasets/il.html) | HUD income-limit areas/counties and household size; rules, not resident counts | FY 2026, effective May 1, 2026; program-specific exceptions | Official tables, spreadsheets and API options | County/household-size income thresholds for a versioned housing-program rules catalog. | 2 |
| FY 2027 Fair Market Rents — HUD | [HUD-FMR-2027](https://www.huduser.gov/portal/datasets/fmr.html) | FMR areas/counties; selected SAFMR ZIP areas are a different product | FY 2027; check areas retaining FY 2026 after reevaluation | Tables and downloadable data | Housing-program payment-standard context by bedroom count, not the district median rent or a guarantee of subsidy. | 2 |
| Statewide Affordable Housing Inventory List — Hawaiʻi HHFDC | [HHFDC-INVENTORY-2026](https://dbedt.hawaii.gov/hhfdc/affordable-rental-housing-inventory/) | Property addresses/points, statewide; assign physical locations to existing district polygons | Updated June 10, 2026 | HTML table and locator map | Find affordable properties near constituents, with population type, units and management contact. | 2 |
| DHS Databook 2025 — Hawaiʻi DHS | [DHS-DATABOOK-2025](https://humanservices.hawaii.gov/wp-content/uploads/2026/03/DHS-Databook-2025.pdf) | Statewide program series; selected county context. Reviewed publication has no legislative-district tables | SFY 2014–2025 and other explicitly dated series; publication December 2025 | PDF | Administrative benefit/participation context for financial assistance, SNAP, Medicaid and other DHS services; distinguish survey tables. | 2 |
| Med-QUEST Application and Enrollment Data — Hawaiʻi DHS Med-QUEST | [MQ-ENROLLMENT](https://medquest.hawaii.gov/posts/med-quest-application-and-enrollment-data) | Published administrative reporting areas; district breakdown not verified | Page June 22, 2026; linked data update June 8, 2026 | Linked reports/data | Actual Medicaid application/enrollment context; retain reporting unit, period and coverage definition. | 2 |
| OASDI Beneficiaries by State and Congressional District: Hawaiʻi — SSA | [SSA-HI-2025](https://www.ssa.gov/policy/docs/factsheets/cong_stats/2025/hi.html) | State and U.S. congressional districts, not Hawaiʻi state House/Senate districts | 2025 edition | HTML tables | Administrative Social Security beneficiaries/payment context, separate from ACS household receipt. | 2 |
| Local Area Unemployment Statistics — DBEDT labor statistics / BLS federal-state program | [LAUS-HI](https://dbedt.hawaii.gov/economic/labor/) | State, counties and islands; selected seasonally adjusted series | Monthly/annual time series; freeze exact release on acquisition | Linked tables/data warehouse | Timely county/state labor trends beyond a five-year ACS snapshot; jobs-at-workplace series remain separate. | 2 |
| Annual population estimates — Hawaiʻi DBEDT State Data Center / Census PEP | [PEP-HI](https://census.hawaii.gov/population-estimate/) | State/county, with age/sex products where published | Annual; select a consistent latest vintage, including July 1, 2025 estimates where published | Official tables | Current county/state demographic trends; not district annual population estimates. | 2 |
| Counties — Hawaiʻi Statewide GIS | [COUNTIES-GIS](https://geodata.hawaii.gov/arcgis/rest/services/Census/MapServer/29) | County polygons | Layer metadata must be frozen on acquisition | ArcGIS REST JSON/GeoJSON | Document county intersections, particularly Maui/Kalawao, without assigning all multi-county districts to one county. | 2 |
| Public schools — Hawaiʻi DOE / Statewide GIS | [SCHOOLS-GIS](https://geodata.hawaii.gov/arcgis/rest/services/Infrastructure/MapServer/7) | School points | As of November 2024 in layer description | ArcGIS REST JSON/GeoJSON | Locate schools in districts; school performance/student enrollment are not resident-district statistics. | 2 |
| Hospitals — Hawaiʻi DOH OHCA / Statewide GIS | [HOSPITALS-GIS](https://geodata.hawaii.gov/arcgis/rest/services/Infrastructure/MapServer/5) | Facility points | As of September 15, 2026 in layer description | ArcGIS REST JSON/GeoJSON | Locate hospitals and published facility capacity; geography of a facility is not its catchment or patient residence. | 2 |
| Comprehensive Housing Affordability Strategy data — HUD | [HUD-CHAS](https://www.huduser.gov/portal/datasets/cp.html) | State/county/place and smaller-area download products; no direct 2022 Hawaiʻi SLD series verified | 2018–2022 release dated December 23, 2025 on reviewed page | Downloads / token-authenticated API | HUD-adjusted income bands × tenure × housing problems; richer affordable-housing need context. | 3 |
| 2020 census tracts — Hawaiʻi Statewide GIS | [TRACTS-GIS](https://geodata.hawaii.gov/arcgis/rest/services/Census/MapServer/31) | Tract polygons clipped to coastline | 2020 geography; 2023 label corrections noted | ArcGIS REST JSON/GeoJSON | Only for a specific tract-only statistic or service-access analysis, not needed for direct ACS SLD tables. | 3 |
| 2020 census block groups — Hawaiʻi Statewide GIS | [BG-GIS](https://geodata.hawaii.gov/arcgis/rest/services/Census/MapServer/26) | Block-group polygons clipped to coastline | 2020 geography | ArcGIS REST JSON/GeoJSON | Smaller-area source geometry for an explicitly approved housing/person allocation model. | 3 |
| ACS five-year Public Use Microdata Sample — Census | [ACS-PUMS](https://www.census.gov/programs-surveys/acs/microdata.html) | State and PUMA are the finest usable identified geographies; no state legislative districts | Use a documented five-year release and consistent PUMA definitions | Person/housing CSV, dictionaries and replicate weights | Custom joint age/living-arrangement/tenure/income analysis at state/PUMA level only. | 3 |
| Hawaiʻi BRFSS / Hawaiʻi Health Data Warehouse — Hawaiʻi DOH | [DOH-BRFSS](https://health.hawaii.gov/brfss/data-access-and-query-system/) | State/county and any specifically documented report geographies; no 2022 SLD coverage verified | Varies by measure and pooled period | HHDW reports; restricted files require agreement | Community health context beyond ACS disability/insurance; sample size and confidentiality may preclude subgroups. | 3 |
| PLACES small-area health estimates — CDC | [CDC-PLACES](https://www.cdc.gov/places/methodology/) | County, place, tract and ZCTA; not direct legislative districts | Release-specific BRFSS/ACS input years; exact release not selected | Data portal downloads / API | Optional modeled chronic-disease context with 95% intervals and explicit spatial-model caveats. | 3 |
| 2020 Census 118th Congressional District Summary File, Hawaiʻi (includes 2022 SLDs) — Census | [CENSUS2020-CD118-HI](https://www2.census.gov/programs-surveys/decennial/2020/data/118th-congressional-district-summary-file/Hawaii/) | 2022 House/Senate districts, with select related geographies | April 1, 2020 Census counts; release August 31, 2023 | Verified directory lists hi2020.cd18.zip (about14 MB), summary files plus technical documentation | Population/household/housing baseline on the 2022 plan without inventing a historical district-ID crosswalk. Compare measurement concepts carefully with ACS period estimates. | 2 |

### C2. Avoid duplicate or misleading additions

1. Do not redownload DP02–DP05 just to unlock existing rows. The [official DBEDT 2024 ACS page](https://census.hawaii.gov/acs/acs-2024/) remains the workbook source/distribution reference.
2. **S0103 is the 65+ population table; S0102 is the 60+ population table.** Use [S0103 metadata](https://api.census.gov/data/2024/acs/acs5/subject/groups/S0103.html) for the requested kūpuna cutoff. Program eligibility may use 60+, so store that as a distinct concept rather than changing it to 65+.
3. Social Security/retirement receipt tables for all households largely duplicate DP03 unless they add a needed cross-tabulation. Receipt and mean benefit income do not measure whether a source is primary.
4. S2201 and B22001 can overlap. Acquire the narrower table only when it adds a needed cell, simpler reproducible definition or denominator; avoid duplicate aliases with unclear precedence.
5. DP02 already answers the responsible-grandparent total. [B10002](https://data.census.gov/table/ACSDT1Y2023.B10002?q=Grandparents+and+Grandchildren) counts **grandchildren** under 18 living with a grandparent householder, not responsible-grandparent people. It is not a substitute for Q23.
6. Existing DP04 includes broad burden and crowding measures; B25070 is needed specifically because the existing 35%+ bin cannot resolve 50%+. B25106 adds income × burden × tenure, not simply another median rent.
7. [ACS Comparison Profiles geography metadata](https://api.census.gov/data/2024/acs/acs5/cprofile/geography.html) lists U.S., state, county, place and metropolitan areas, **not state legislative districts**. Do not promise direct SLD Comparison Profiles.
8. The [DBEDT Data Book](https://dbedt.hawaii.gov/economic/databook/) is valuable for county/state history, but many ACS republications would duplicate imported data. Select a named nonduplicative series and its edition instead of importing every chapter. The source registry’s older candidate is not the current imported statistical inventory.
9. The [2024 Hawaiʻi Housing Planning Study](https://dbedt.hawaii.gov/hhfdc/hhps-landing-page/) adds county/state survey and housing-need context. Its estimates/projections cannot be relabeled as district ACS counts; defer full extraction until a specific question needs it.

### C3. Genuine joint measures and unsupported combinations

| Required combination | Verified published route | Correct interpretation / remaining gap |
| --- | --- | --- |
| Age × poverty | B17001; B17024 for income-to-poverty ratios | Person-based poverty universe; both subgroup counts and denominators must match |
| Age of householder × household income | B19037 | Households, not all older individuals’ own income |
| Age of householder × tenure | B25007 | Household measure; all older residents’ tenure is a different universe |
| Older householder × living alone × tenure | B25011 | Genuine three-way cells. Published `B25011_021E/M` and `_045E/M` identify owner/renter one-person households with householder 65+ |
| Adult age × living arrangements | B09021 | Adults in households; no primary-income dependence condition |
| Sex × age × disability | B18101 | Civilian noninstitutionalized people, not all residents including nursing facilities |
| Income bracket × tenure × housing-cost share | B25106 | Published joint cells; coarse bins limit threshold precision |
| Poverty × SNAP receipt | B22003 / relevant S2201 cells | Household poverty/receipt, not SNAP eligibility or all food insecurity |
| Presence of person 60+ × SNAP receipt | B22001 / S2201 | Age60+ household-presence condition, not a count of 65+ SNAP recipient individuals |
| Older-householder household × Social Security receipt | S0103 household section | At least one household recipient; no primary-source share |
| Grandparent responsibility × selected caregiver characteristics | S1002 | Read each column’s denominator; total caregiver count already exists locally |
| Older, alone, renter **and primarily Social Security dependent** | No verified published district table supplies all conditions | B25011 supplies the first three; adding an unrelated Social Security marginal does not supply the fourth |

API labels/columns must be checked rather than inferring a variable from a workbook label. B25106’s title is “Tenure by Housing Costs as a Percentage of Household Income…” and its indexed official metadata includes nested income brackets; direct metadata requests repeatedly timed out during this study. Its identity is verified, but full label/unit and Hawaiʻi coverage validation is still pending. Do not ship guessed cell mappings.

### C4. Coverage beyond the30 examples

| Domain | Reuse first | Targeted extension / what remains unavailable |
| --- | --- | --- |
| Demographics | DP05 population, sex, age and race/ethnicity; DP02 marital status, migration, language and household composition |2020 Census CD118 Hawaiʻi file supplies a2022-plan baseline; a single ACS period cannot show a trend. No new generic demographic profile needed |
| Economic conditions | DP03 income distribution, employment, labor force, occupation/industry, SS/retirement/SSI/cash/SNAP receipt | B19037 age-householder income; B17001/B17024 poverty subgroups. DBEDT budgets add a cost standard, not a district hardship count. LAUS adds timely county/state labor context |
| Housing | DP04 tenure, households, crowding, housing age, values, mortgage/rent costs and broad burden | B25070 severe burden; B25106 income/burden combinations; B25008 person tenure; HHFDC properties for referrals. Eviction/arrears and live vacancies remain unverified |
| Kūpuna | Age share/count, broad older disability, older poverty rate, older-alone components | B25007/B25011/B19037/S0103 add valid household cross-tabs; no full older-alone-renter-primary-SS count |
| Children/families/education | DP02 household children, family types, grandparents, school enrollment and25+ education; DP05 under 18 | B17001 child-poverty counts and S1002 caregiver detail. DOE reports describe enrolled pupils/schools, not district-resident attainment; no direct childcare unmet-need count verified |
| Health/disability | DP02 broad disability and DP03 health insurance | [B27001](https://api.census.gov/data/2024/acs/acs5/groups/B27001.html) adds age/sex insurance coverage; B18101 adds age/sex disability. BRFSS/PLACES remain optional native-geography context/modeling |
| Transport/digital access | DP03 commuting mode/time, DP04 vehicles, DP02 computers/broadband subscription | [B28004](https://api.census.gov/data/2024/acs/acs5/groups/B28004.html) adds household-income × internet-subscription. Subscription is not network availability; a no-vehicle household is not necessarily unable to access services. Route/travel-time analysis needs a separate maintained network use case |
| Government programs | Existing need signals; no directory imported | Verified rule/application directory, then deterministic versioned screening. Administrative caseloads remain separate from ACS survey receipt |
| Community planning | Current needs snapshot and existing polygons | County/state PEP/LAUS, carefully chosen facility locations and a2020 baseline; comparable district history or modeled service access requires explicit methods |

The [official Hawaiʻi CD118 directory](https://www2.census.gov/programs-surveys/decennial/2020/data/118th-congressional-district-summary-file/Hawaii/) lists `hi2020.cd18.zip` at about14 MB. This is a verified optional download, **not downloaded in this study**. It retabulates2020 Census demographics/housing to the2022 districts; it supplies no income or poverty data. Census disclosure protection/coverage considerations still apply, and comparing an April1,2020 count with a2020–2024 survey estimate is not a clean annual-growth measurement.

## D. Program Information Catalog

### D1. What program data must represent

Create a directory of programs and rule versions, separate from resident statistics. At minimum store official name, benefit/purpose, administering agency, funding/administration classification, intended population, household/assistance-unit definition, age, countable-income rules, household-size thresholds, resource tests/exclusions, residency/status conditions, disability/functional criteria, service area, official application path, local offices, document citations, verification date, rule effective interval, application window, waitlist/capacity status and public participation sources.

A missing numerical threshold or effective date must remain **unknown**, not become “no restriction.” The linked **`program-information-catalog.md`** and JSON contain 16 initial program/directory records with these fields and explicit outstanding verification tasks. They are source-discovery records, not executable eligibility rules.

| Program / official source | Agency / classification | Purpose / eligibility unit | Version and application availability | Geography / administrative statistics |
| --- | --- | --- | --- | --- |
| [Supplemental Nutrition Assistance Program (SNAP)](https://humanservices.hawaii.gov/bessd/snap./) | USDA; Hawaiʻi DHS BESSD; Federal, state administered | Food purchasing benefits through EBT. Low-income food-purchase/preparation units, with age/disability exceptions. | DHS chart 10/1/2026; current categorical/work-rule details require their own effective versions. Applications linked; case approval not implied. | Statewide DHS monthly participation links and annual databook; no 2022 SLD administrative series verified. |
| [Supplemental Security Income (SSI)](https://www.ssa.gov/ssi/text-eligibility-ussi.htm) | Social Security Administration; Federal | Means-tested cash support. People 65+, or blind/disabled adults and eligible children. | 2026 guidance; preserve announced 2027 rules separately from rules effective now. Application/appointment routes available; not a benefit guarantee. | U.S. including Hawaiʻi SSA state/county SSI publications should be selected/versioned; published OASDI congressional counts are a different population. No SLD file verified. |
| [Aid to the Aged, Blind or Disabled (AABD)](https://humanservices.hawaii.gov/bessd/fnsrandr/) | Hawaiʻi DHS BESSD; State financial assistance | Cash support for qualifying aged/blind/disabled residents. People 65+ or meeting blindness/permanent-disability criteria. | Current overview verified; current numeric income/resource schedule and controlling HAR effective version not fully verified. Financial-assistance application route published. | Statewide AABD statewide series in DHS Databook 2025; no SLD publication verified. |
| [Medicaid / QUEST Integration](https://medquest.hawaii.gov/en/resources/rules-and-policy) | Hawaiʻi DHS Med-QUEST; CMS; Federal-state | Health coverage and category-specific services. Qualifying children, pregnant people, adults and aged/blind/disabled categories. | 2026 standards chart listed effective 1/13/2026; attachment returned 403 during research. KOLEA application route published; eligibility category must be determined. | Statewide Official Application and Enrollment Data page and CMS state reports; district coverage not verified. |
| [Medicare Savings Programs: QMB, SLMB, QI, QDWI](https://www.medicare.gov/basics/costs/help/medicare-savings-programs) | Hawaiʻi Med-QUEST; CMS; Federal-state | Help with specified Medicare premiums and, for QMB, covered cost sharing. Medicare-entitled people meeting the particular program conditions. | Federal2026 page verified; Hawaiʻi current program chart requires separate review. Apply through state; QI allocation/annual rules differ. | Statewide CMS/Med-QUEST aggregate data if separately published; no SLD MSP series verified. |
| [Medicare Part D Extra Help](https://www.ssa.gov/medicare/part-d-extra-help) | SSA and CMS; Federal | Reduces prescription-drug coverage costs. Medicare beneficiaries with limited income/resources; categorical routes also exist. | Current official page; exact2026 Hawaiʻi income/resource chart not extracted. SSA states application can be made any time before/after PartD enrollment. Direct form redirected to a service message during research. | U.S. including Hawaiʻi CMS low-income-subsidy state/county products may be relevant; exact release not selected; no SLD verified. |
| [Older Americans Act / EOA home and community services](https://health.hawaii.gov/eoa/home/home-and-community-services/) | Hawaiʻi DOH EOA and county offices on aging; Federal-state/local service network | Nutrition, transport, personal care, case management and related supports. Generally adults 60+; individual services have additional functional/need criteria. | Current service page; contract-specific eligibility and capacity versions not extracted. County intake/referral; service capacity and waiting lists require confirmation. | Statewide through county networks EOA/state-plan and county reporting; no public2022 SLD participation series verified. |
| [Kūpuna Care](https://elderlyaffairs.com/services/) | Hawaiʻi EOA and county aging agencies; State | Home/community supports to help older adults remain at home. Older adults 60+ with assessed functional needs. | Current county/EOA pages; exact contract/rule effective dates not verified. Assessment/referral; slots not verified. | Statewide program, county-administered County/EOA aggregate reporting if published; no SLD series verified. |
| [Hawaiʻi Home Energy Assistance Program (H-HEAP; LIHEAP source family)](https://humanservices.hawaii.gov/bessd/liheap/) | Hawaiʻi DHS and island Community Action Agencies; HHS federal funding; Federal-state/local | One-time utility payment through Energy Credit or Energy Crisis Intervention. Income-qualified households with utility responsibility; crisis route requires shutoff/crisis evidence. | 2026 packet verified; currentFY2027 income chart not verified as ofOct26. EC annualJune1–30 window is past; ECI accepts year-round subject to limited monthly approvals. | Statewide via island agencies Federal/state program summaries may provide aggregate recipients; no SLD series verified. |
| [Housing Choice Voucher / Section8](https://hpha.hawaii.gov/how-to-apply) | HUD; HPHA and separate county public housing agencies; Federal, locally administered | Rental assistance subject to local program rules, funding and admission. Qualifying low-income applicant households. | HUD FY 2026 limits effectiveMay1,2026; current local admissions plan version not extracted. HPHA Oʻahu HCV waitlist explicitly CLOSED on reviewed page. Other administrators must be checked separately. | HPHA HCV listed here servesOʻahu; other county administrators require separate records. HUD/PHA administrative reports generally agency/county/project-based; no 2022 SLD series verified. |
| [Federal and state public housing](https://hpha.hawaii.gov/how-to-apply) | HPHA; HUD for federal programs; Federal and state, distinct program branches | Income-related public housing admission and rent. Applicant households meeting program/site requirements. | Current page verified; federal/state admissions policy versions not extracted. Oʻahu federal-public-housing waitlists CLOSED. Neighbor-island paper-contact route published; unit availability not guaranteed. | Properties statewide, with separate program/site lists. HPHA annual/project reports if selected; no resident SLD enrollment series verified. |
| [Affordable rental properties (directory, not one benefit program)](https://dbedt.hawaii.gov/hhfdc/affordable-rental-housing-inventory/) | HHFDC and individual property/program administrators; Mixed federal/state/county/private program inventory | Find income-restricted family, elderly and special-needs properties. Property-specific target groups and applicant households. | Inventory updatedJune10,2026; eligibility/effective dates must be captured per property. Contact property; inventory does not report current vacancies or open waiting lists. | Property locations statewide; geographic placement is not service restriction. Inventory units are supply counts, not enrolled district residents. |
| [Special Supplemental Nutrition Program for Women, Infants and Children (WIC)](https://health.hawaii.gov/wic/program_details/) | USDA and Hawaiʻi DOH WIC; Federal, state administered | Nutrition benefits, breastfeeding support and referrals. Pregnant/postpartum/breastfeeding people, infants and children under 5 with nutritional risk. | Federal guidelines effectiveJuly1,2026–June 30,2027; state chart adoption/amounts need confirmation. Clinic appointment/referral published; current appointment slots not verified. | Statewide clinic network USDA state WIC data; historical counts on DOH overview are not current enrollment and must not be reused. No SLD series verified. |
| [Temporary Assistance for Needy Families / TAONF](https://humanservices.hawaii.gov/bessd/fnsrandr/) | Hawaiʻi DHS BESSD; federal TANF component and state TAONF; Federal/state financial-assistance branches | Cash assistance and employment-related supports for eligible families. Families with dependent children. | Overview verified; current schedules and complete amended HAR not verified. Financial-assistance application published. | Statewide DHS Databook financial-assistance series statewide; no SLD series verified. |
| [Child Care Subsidy (formerly Child Care Connection Hawaiʻi)](https://humanservices.hawaii.gov/bessd/ccch-subsidies/) | Hawaiʻi DHS BESSD / CCDF; Federal-state | Helps eligible families pay approved childcare costs. Eligible children and families meeting income/activity or exception rules. | Current program page; CCDF planFFY2025–2027. Numeric eligibility/reimbursement schedule version not extracted. Application portal published; subsidy/provider availability requires confirmation. | Statewide DHS/CCDF aggregate reporting; no SLD series verified. |
| [Preschool Open Doors (POD)](https://humanservices.hawaii.gov/preschool-open-doors-application-period-opens-for-2026-2027-school-year/) | Hawaiʻi DHS; PATCH contractor; State preschool tuition assistance | Preschool tuition support. Published2026–27 child birthdate cohortAug1,2021–July 31,2024; kindergarten-entry condition also applies. | HAR17-799.1 effectiveMay29,2026;2026–27 school-year limits. PublishedMay29,2026–May 31,2027 application window, or until funding capacity reached; remaining capacity not verified. | Statewide eligible providers DHS reports may provide aggregate recipients; no SLD series verified. |

### D2. Time-sensitive findings that matter for implementation

- DHS publishes a Hawaiʻi SNAP income chart effective **October 1, 2026**. It distinguishes standard, BBCE and net-income rules; one generic cutoff is insufficient. Use the [current state SNAP page](https://humanservices.hawaii.gov/bessd/snap./) and preserve its dated rule branches.
- Med-QUEST lists a **2026 standards chart effective January 13, 2026**. The linked PDF returned HTTP 403 during research; its numeric cells were not verified. [The official rules page](https://medquest.hawaii.gov/en/resources/rules-and-policy) is verified; obtain/review the attachment before encoding category-specific limits.
- SSI’s resource tests, countable income and [federal maximum payment](https://www.ssa.gov/oact/cola/SSIamts.html) are different concepts. A 2027 amount already announced is not the amount effective in October 2026.
- [Medicare Savings Programs](https://www.medicare.gov/basics/costs/help/medicare-savings-programs) explicitly note higher income limits for Hawaiʻi. Do not use the generic national chart as the Hawaiʻi rule. Store QMB, SLMB, QI and QDWI as distinct rule branches.
- [HPHA’s application page](https://hpha.hawaii.gov/how-to-apply) lists **Oʻahu HCV and Oʻahu federal public-housing waitlists as closed**. It provides neighbor-island paper/contact routes. Availability must be separate from eligibility and service area.
- [H-HEAP](https://humanservices.hawaii.gov/bessd/liheap/) has a June Energy Credit window and a year-round, capacity-limited crisis route. Its 2026 packet does not by itself verify every FY 2027 rule.
- The [POD 2026–27 announcement](https://humanservices.hawaii.gov/preschool-open-doors-application-period-opens-for-2026-2027-school-year/) publishes a birthdate cohort, family-size income schedule and application window through May 31,2027 or funding capacity. Store the cohort/window, not only a floating age label.
- [The WIC clinic directory](https://health.hawaii.gov/wic/clinic-locations/) is the application/referral route. Historic participation figures on an agency overview must not be reused as current enrollment. Federal [2026–27 WIC guidelines](https://www.fna.usda.gov/wic/fr-042926) require the correct Hawaiʻi schedule and state adoption details.

### D3. Separate five different claims

| Claim | Evidence required | Safe DistrictIQ wording |
| --- | --- | --- |
| Potential district need | Published statistics with compatible universe/period | “The district has an estimated X cost-burdened renter households.” |
| Program relevance | Need signal plus verified program purpose/service area | “This program may be relevant to some residents facing this need.” |
| Individual eligibility | Current deterministic rules and sufficiently complete individual/assistance-unit inputs | “These provided facts meet the checked conditions; the agency makes the eligibility determination.” |
| Actual participation | Administrative enrollment/benefit records with period and residence geography | “The agency reports X enrolled units in this reporting area.” |
| Potentially underserved population | Compatible eligible-population estimate and unduplicated participation for the same units/area/period | Requires additional methodology; cannot subtract a county caseload from a district ACS proxy |

No public **2022 state legislative-district administrative participation series** was verified for the initial programs in the reviewed sources. This is a documented research result, not a claim that no agency possesses such data. The [DHS annual-report catalog](https://humanservices.hawaii.gov/reports/annual-reports/) and reviewed Databook supply larger-area/temporal context. The [Med-QUEST enrollment page](https://medquest.hawaii.gov/posts/med-quest-application-and-enrollment-data) provides administrative reporting, with exact attachment geography requiring further QA. [SSA’s Hawaiʻi congressional publication](https://www.ssa.gov/policy/docs/factsheets/cong_stats/2025/hi.html) refers to U.S. congressional districts, not the 51/25 state districts.

USDA’s [SNAP data tables](https://fns-prod.azureedge.us/pd/supplemental-nutrition-assistance-program-snap) and CMS’s [Medicaid enrollment reports](https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-chip-enrollment-data/monthly-medicaid-chip-application-eligibility-determination-and-enrollment-reports-data) are useful aggregate administrative sources; choose exact files/periods before ingestion. Neither establishes district eligibility. CMS county or Medicare Advantage products also must not be labeled as all Medicare beneficiaries.

If district participation is needed later, request agency-produced **aggregate counts by residence in the 2022 plan**, with definitions, period, deduplication, suppression and coverage documentation. Do not obtain personally identifiable benefit records for this dashboard. Public office/project locations can support referrals now but do not show where their clients live.

### D4. Matching and RAG recommendation

Use deterministic, versioned checks for conditions that have been verified. Match district-level need **themes** to program purposes; show the matching indicators, service area, status and rule-version citations. Keep individual screening optional and separate, returning `unknown` when inputs or verified rules are missing. Let AI explain the evidence and rule outcomes; it should not invent or reinterpret numerical eligibility thresholds.

A structured program directory and official links are sufficient for the initial program-information answers. RAG becomes useful only for longer policy manuals, exceptions and explanatory documents that cannot reasonably be captured in structured fields. Retrieved excerpts must retain section/page, effective date and source. RAG should explain rules; it should not override a validated rule engine or become a prerequisite for every referral.

## E. Geographic Compatibility Assessment

### E1. Classification

| Class | Sources in this plan | District use |
| --- | --- | --- |
| 1: Direct 2022-plan-compatible SLD statistics | Existing2024 DP02–05; selected2024 detailed and subject tables | Preferred; join Census state/chamber/district identifiers directly, not spatially |
| 2: Tract/block-group sources | Selected detailed ACS products, CHAS smaller-area extracts, tract PLACES; corresponding polygons | Only allocate when direct SLD estimates do not exist and methodology is approved |
| 3: County | DBEDT budgets, PEP/LAUS, selected administrative reports, HUD limits/FMR/CHAS | Display as county context/rules; never relabel as district observations |
| 4: State | Many administrative series, program rules, selected surveys | State benchmark or service rule, not district prevalence |
| 5: Other geography | PUMA microdata, U.S. congressional SSA tables, school/facility/property points, FMR areas, ZIP/ZCTA products | Use at their native geography; points can be located inside a district but do not describe its residents |
| 6: Not usable for the requested district statistic | National findings without a local estimate, unsupported joint counts, unverified program caseload geographies | Explain unavailability; do not create false precision |

The [2024 Subject Tables geography listing](https://api.census.gov/data/2024/acs/acs5/subject/geography.html) explicitly includes upper chamber610 and lower chamber620, county and tract. It does **not** list block groups. Do not assume every ACS product has the same finest geography. The [Census legislative-district documentation](https://www.census.gov/programs-surveys/decennial-census/about/rdo/state-legislative-district. 2022.html) provides the authoritative plan/relationship-file starting point.

### E2. Identifier and boundary rules

Use state FIPS `15`, the chamber and zero-padded district number. House 30 is Census lower-chamber code `030`, mapped through a validated registry to existing `house-30`; Senate 15 is upper-chamber `015` to `senate-15`. Store the Census geographic code/summary level as well as the existing friendly identifier. Avoid name-only joins and avoid assuming worksheet labels alone prove plan compatibility.

For each acquisition, validate exactly House 01–51 and Senate 01–25, all county codes including15005 Kalawao where published, reference period, source release and boundary compatibility. Review changes for each new release; do not carry the 2024 compatibility decision forward automatically.

Existing district `county` is a source label, not a population allocation. For multi-county districts, show each intersecting county as a separate benchmark with a documented intersection/containment rule. Do not average county medians or claim a single “corresponding county” without qualification. County geometry is useful specifically to validate Maui/Kalawao intersections and identify source-label simplifications.

The current comparison service maps `OAHU` to Honolulu and supplies **both Maui and Kalawao as separate regional contexts for a `MAUI` label**, explicitly without claiming exact intersection or combining their estimates. Preserve that caution until a verified county relationship or geometry check establishes a more precise relationship.

### E3. When allocation is appropriate

Prefer directly published SLD estimates even when tract files are easy to obtain. For an additive count available only on smaller source areas:

1. Use a complete, compatible block-to-district or finer geographic relationship where available. Entire contained units can be aggregated without fractional allocation, although ACS sampling uncertainty remains.
2. For split source areas, **population weights** may be appropriate for person counts, preferably matched to the subgroup if trustworthy counts exist. Total-population allocation of older-adult poverty assumes the subgroup is distributed similarly within the source area; that assumption can fail.
3. Use **occupied-housing/household weights** for household counts, and occupied renter units when a renter-specific allocation is justified. An all-population weight is not automatically appropriate for rental housing.
4. Reserve **area weights** for genuinely area-based measures or an explicitly labeled fallback. They are especially weak in Hawaiʻi because uninhabited land, mountains and coastal geography create uneven settlement. The existing area-crosswalk demonstration is not a validated demographic allocation method.
5. Allocate compatible numerators and denominators separately; recompute rates. Do not average percentages or allocate medians as if they were additive. County median minus district median is meaningless.

Every allocated result needs source/target vintages, weight basis/date, allocation method, coverage/sliver checks and a separate `modeled/allocated` status. A propagated ACS MOE covers sampling error under its calculation assumptions; it does not capture ecological allocation bias or uncertainty in weights. Do not display it as a complete uncertainty interval.

For service access, point-in-polygon can answer “Which clinics are physically in this district?” Travel-time or accessibility claims additionally need a maintained transport network, schedules, departure-time/mode assumptions and origin populations. Neither straight-line distance nor a facility inside a district establishes access for all residents. No transport dataset is mandatory before the direct statistical expansion.

## F. Missing Data and Statistical Limitations

### F1. Questions that remain unsupported after the first ten tables

- Exact district counts of older adults primarily dependent on Social Security, especially jointly alone and renting. No verified district table supplies the needed full intersection and primary-income definition.
- Exact numbers of families unable to afford basic necessities under a composition-specific budget. DBEDT budgets are useful standards, but current district marginals lack the joint family-composition/income/cost distribution.
- Counts of residents or households individually eligible for SNAP, Medicaid, SSI or housing assistance. Assets, deductions, assistance units, status, disability and other conditions are not all observed in public aggregate ACS cells.
- A unique population at imminent risk of eviction, homelessness or housing instability. Cost burden/crowding are measured factors, not a validated outcome prediction; no suitable district arrears/eviction outcome series was verified.
- Exact “rest of Honolulu County” median rents or incomes from a district and county median. A distribution or independently tabulated remainder is needed.
- Annual district trends from the single imported2020–2024 period; consistent geography and comparable prior releases are needed.
- Counts of unmet eligible program need by subtracting overlapping or geographically mismatched estimates and administrative totals.

### F2. Statistical quality rules

1. Preserve original estimate, MOE, percent, percent-MOE and annotation separately. `(X)`, suppression, not-computed cases, rounded zero and unavailable values have different meanings. API sentinel values must be decoded using the release’s documentation, never treated as substantive negative counts.
2. Store universe/denominator, age limits and time basis for every measure. Civilian noninstitutionalized disability, total residents, poverty-determined population, households, families and housing units are different universes.
3. Prefer a published aggregate and its MOE. When summing disjoint cells, a documented approximate MOE is often `sqrt(sum(MOE_i²))`; label it derived and note covariance assumptions. Ratios/proportions require their appropriate Census method, not the same formula applied indiscriminately. Use a published percentage/MOE when it matches the requested denominator. See the [2020–2024 accuracy documentation](https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf).
4. Do not add unrelated marginals to find a union, multiply shares to find an intersection, or join aggregate tables as if they were individual records. Only sum disjoint compatible cells or use a directly published union, such as B19058’s specified cash-assistance-or-SNAP measure.
5. ACS MOEs conventionally express90% confidence; a proposed local reliability flag is a product policy, not a Census suppression rule. Retain the value with a warning when appropriate. Any CV threshold must be documented, and undefined CV at zero needs explicit handling.
6. State/county benchmarks containing a district are correlated with it; household/person subgroups and overlapping ACS periods can also be correlated. A point difference is descriptive unless a valid uncertainty comparison is applied. Use [Census statistical-testing guidance](https://www.census.gov/programs-surveys/acs/guidance/statistical-testing-tool.html), not an automatic claim of meaningful difference whenever point estimates differ.
7. Household income is annual and rent is monthly. Income amounts in this release are expressed in2024 inflation-adjusted dollars. A ratio of medians across different universes is a contextual benchmark, not observed housing burden.
8. Broad bins limit exact thresholds: DP04 supports30%+ and35%+ categories; B25070 supplies50%+. A strict “greater than” request cannot always be separated from the boundary value in a published bin.
9. “Neighboring” must mean a documented same-chamber spatial adjacency rule. “Biggest” age groups need count/share labels because the age bins have unequal widths. “Higher” does not mean causation or individual behavior.
10. Race-alone, race-in-combination and Hispanic origin cannot be indiscriminately added. Disability/insurance, school enrollment, vehicle access and broadband each have their own denominator and operational definition.

### F3. Limits of microdata and health sources

[ACS PUMS](https://www.census.gov/programs-surveys/acs/microdata.html) allows custom person/housing-unit analyses, but identified geography stops at [PUMAs of at least100,000 people](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/pumas.html). It cannot establish reliable House/Senate district counts by assigning PUMA estimates to smaller districts. Custom state/PUMA analysis requires the proper person/household linkage, weights, replicate weights, treatment of negative/zero income, benefit reference periods and disclosure/sampling checks. It remains a separately labeled advanced analysis.

[Hawaiʻi DOH BRFSS access](https://health.hawaii.gov/brfss/data-access-and-query-system/) points to HHDW reporting and restricted-data processes. Verify each report’s actual boundary vintage and pooled period; this study did not verify a2022-plan SLD health series. [CDC PLACES](https://www.cdc.gov/places/methodology/) supplies model-based county/place/tract/ZCTA health estimates with95% intervals. These are not directly measured legislative-district ACS statistics; spatially reallocating them requires an additional model and cannot erase that distinction.

## G. Recommended Database Extensions

### G1. Preserve what works

The current `Statistic` already holds geography level/vintage, indicator, estimate/MOE, unit, period, variable list, method, status, source and provenance. `ACSProfileObservation` preserves workbook row/section, four measure columns, raw strings and provenance. `Source.metadata_record` can hold release metadata. Reuse these rather than rebuilding the dashboard or flattening all original observations into46 aliases.

The missing elements are primarily **semantic metadata**: canonical indicator definitions, universe/denominator references, native Census variable IDs, supported dimensions, measure roles, explicit confidence level/annotation meanings, release-level update/verification metadata and controlled calculation recipes.

### G2. Minimal statistical path

1. **First, a reviewed metadata registry in the existing code/data configuration.** Give each approved measure a stable ID, label/synonyms, topic, source locator, universe, unit, count/percent/median/mean role, period/vintage compatibility, denominator ID and supported subgroup dimensions. Resolve repeated worksheet labels through section/row and workbook version. Do not infer native API variable IDs from Excel row numbers.
2. **Reuse existing observations for initial raw retrieval.** A curated locator can point to `source_id + geography_id + profile + row_number + reference_period` and select the appropriate reported measure. This does not require reimporting workbooks or duplicating every raw value in `statistics`.
3. **When detailed-table ingestion starts, add one additive native-observation table if needed.** Suggested key: `(dataset_release_id, native_geography_id, variable_id)`. Store estimate/MOE, reported annotations, unit/measure role, confidence level, source/table ID and provenance. Keep original API response/CSV unchanged on disk. Detailed-table observations should not be forced into an Excel `row_number` schema.
4. **Promote release/indicator metadata to tables only when useful.** An `indicator_definitions` registry and `dataset_releases` table can replace the reviewed configuration without changing stable IDs. Release metadata should include product/year/period, geography vintage/compatibility decision, official landing/download/API URLs, retrieved/verified dates, file hashes, expected update cadence and QA status. A release is not approved merely because it was discovered.
5. **Define derived measures declaratively.** Store input observation IDs, allowed sum/ratio/difference, unit/denominator constraints, MOE method, exclusions and versioned formula in metadata. The server calculates; the model chooses among approved recipes. Native values and derived values must remain distinguishable.

Existing APIs and46 dashboard aliases should continue to resolve the same values. The existing uniqueness rule on `statistics` does not include geography vintage; before storing multiple boundary plans under one source/period, introduce a release/geo identity that prevents accidental overwrites. This is a future migration concern, not a reason to migrate during research.

A canonical geography registry becomes useful for county geometry, native GEOIDs and multiple vintages. It can initially map to existing `District` IDs and county/state strings. Do not require a wholesale district-table redesign before adding direct ACS tables.

### G3. Metadata-driven chatbot retrieval

Recommended read-only tool sequence:

1. `search_indicators(query, geography_level, period, requested_dimensions)` returns a bounded set of **approved** definitions, universes and availability statuses.
2. `describe_indicator(indicator_id)` explains source/table, units, denominator, age cutoff, supported combinations and missing values.
3. `get_observations(geography_ids, indicator_ids, period)` retrieves bounded native facts with MOEs, annotations and source cells/variables.
4. `calculate_statistic(recipe_id, geography_ids)` executes only reviewed formulas; no model-generated expressions or SQL.
5. Existing comparison tools use the same definition/unit/period checks, with an optional same-chamber spatial-neighbor resolver.

Keep server-side evidence references and deterministic number/citation rendering. Validate IDs, query size, returned rows, timeouts and approved source status; use a database role with SELECT-only permissions for model-facing retrieval where feasible. New-source provenance must not be blocked by a hardcoded old-source filter, but source expansion should occur through explicit approval metadata rather than accepting arbitrary sources.

For compound questions, search for a **single supported joint measure** or a valid recipe over disjoint joint cells. If none exists, return which dimensions are missing, offer a valid reformulation and explain the limitation. Do not retrieve separate marginals and let the model improvise an intersection.

### G4. Program and administrative additions, later

Use small additive entities such as `Program`, versioned `ProgramRuleSet` and `ServiceLocation`. Store rule expressions/threshold schedules with effective intervals and cited sections. A point location’s district intersection is separate from the program’s service area. Program-to-need relevance can be reviewed metadata mapping indicator themes to programs, with a saved explanation of the match.

Administrative participation belongs in a separate observation type or a clearly typed dataset, with program, geography, reporting period, unit, stock/flow definition, deduplication and suppression metadata. Enrollment households, recipients, monthly cases and annual unduplicated people cannot be treated as interchangeable ACS estimates. No program table needs to be implemented before raw statistical retrieval is reliable.

## H. Prioritized Download Checklist

### H1. Reuse first — zero new downloads

- [ ] Expose reviewed raw rows for education, disability, older poverty **rates**, older living alone, grandparents, SNAP/SSI/SS receipt, household children, vehicles and broadband.
- [ ] Add approved derived recipes for income below $50,000, older-alone total and comparable housing-burden totals/percentages; preserve MOE assumptions and exclusions.
- [ ] Test the30 question intents and unsupported joint requests against actual database evidence. Availability in this report is not a claim those new retrieval paths are already implemented.

### H2. First targeted ACS acquisition

All paths below are relative to **`/Users/gianvelasco/Desktop/HAIC26`** and are proposed storage locations, not claims that files already exist. Source links are the exact verified table-metadata/download entry points; `data.census.gov` can export a chosen table/geography toCSV. Use one source release consistently for all 76 districts and comparison geographies.

| Order | Retrieve / official location | Why / question coverage | Geographic coverage | Proposed project location | Timing |
| --- | --- | --- | --- | --- | --- |
| 1 | [B17001](https://api.census.gov/data/2024/acs/acs5/groups/B17001.html) | Poverty counts/universes; Q3,10,21,25,27 | HI lower/upper SLD, county/state | `data/raw/acs/2024/detailed/B17001/` | First controlled import in the implementation phase |
| 2 | [B25070](https://api.census.gov/data/2024/acs/acs5/groups/B25070.html) | Severe renter burden; Q13,16,17,26 | Same | `data/raw/acs/2024/detailed/B25070/` | First batch |
| 3 | [B25007](https://api.census.gov/data/2024/acs/acs5/groups/B25007.html) | Older-householder tenure; Q4 | Same | `data/raw/acs/2024/detailed/B25007/` | First batch |
| 4 | [B25011](https://api.census.gov/data/2024/acs/acs5/groups/B25011.html) | Older-alone × tenure; Q4,6,25 | Same | `data/raw/acs/2024/detailed/B25011/` | First batch |
| 5 | [B19037](https://api.census.gov/data/2024/acs/acs5/groups/B19037.html) | Age-householder × income; Q1 proxy, 9,25 | Same | `data/raw/acs/2024/detailed/B19037/` | First batch |
| 6 | [B25008](https://api.census.gov/data/2024/acs/acs5/groups/B25008.html) | Person-based tenure; Q14 | Same | `data/raw/acs/2024/detailed/B25008/` | Next small batch |
| 7 | [S0103](https://api.census.gov/data/2024/acs/acs5/subject/groups/S0103.html) | Coherent65+ profile and older-householder receipt context; Q1 proxy, 25,28 | Same; product geography verified | `data/raw/acs/2024/subject/S0103/` | Next batch, curate mixed universes first |
| 8 | [S2201](https://api.census.gov/data/2024/acs/acs5/subject/groups/S2201.html) | SNAP household cross-tabs; Q12,27,29 | Same | `data/raw/acs/2024/subject/S2201/` | Next batch; check percent-column denominators |
| 9 | [B19058](https://api.census.gov/data/2024/acs/acs5/groups/B19058.html) | Defined cash-assistance-or-SNAP union; Q12 | Same | `data/raw/acs/2024/detailed/B19058/` | Next batch |
| 10 | [B25106](https://api.census.gov/data/2024/acs/acs5/groups/B25106.html) | Income × tenure × burden; Q8,16,26 | Same; cell QA pending | `data/raw/acs/2024/detailed/B25106/` | Next batch after successful metadata/coverage validation |

For each folder retain `metadata.json`/table shell, the native response orCSV, annotations, retrieval manifest, source URL, period, hashes and QA results. A source’s failure or timeout is not an empty dataset.

**Census access:** Census now requires an activated API key for **data queries**; metadata queries can be keyless. See the [official May 2026 announcement](https://www.census.gov/library/video/2026/adrm/requesting-a-census-data-api-key.html), [June clarification](https://content.govdelivery.com/accounts/USCENSUS/bulletins/41aaf23), and [free key registration](https://api.census.gov/data/key_signup.html). Keep the key server-side and redact it from provenance/logged URLs. This is a Census key, separate from the existing OpenAI key. It is not needed to read already imported PostgreSQL data or to use manualCSV export.

A proposed request shape, **not executed acquisition code**, is:

```text
GET https://api.census.gov/data/2024/acs/acs5
  get=NAME,group(B17001)
  for=state legislative district (lower chamber):*
  in=state:15
  key=<server-side Census key>
```

URL-encode parameters through an HTTP client; repeat upper-chamber and county/state scopes, or use subject-product base paths for S tables. Validate response schema, HTTP redirects and expected geography coverage before treating a request as successful.

### H3. High-value acquisitions after the first statistical batch

- [ ] Select **B18101, B09021, B17024, B22003 and S1002** only for the additional subgroup combinations in sectionC; store under the matching `data/raw/acs/2024/{detailed,subject}/<table>/` paths. B22001 is an optional narrower alternative when S2201 is sufficient, not a mandatory duplicate.
- [ ] Select **B27001** for insurance by age/sex or **B28004** for internet subscription by household income only when those cross-tabs are requested; use the same 2024 detailed-table folder structure. Existing overall insurance/broadband observations do not need reimporting.
- [ ] For a2020 planning baseline, the verified **`hi2020.cd18.zip`** file in the official Hawaiʻi CD118 directory can be stored in `data/raw/census/2020/cd118/hawaii/` with its technical documentation. Select the needed demographic/housing table before ingesting; this does not supply ACS-like income or an annual trend.
- [ ] Curate the official program records in sectionD into `data/raw/programs/<agency>/<program>/<effective-version>/`, keeping source snapshots, rule extracts, dates and verification notes. Start with SNAP, SSI/AABD, Med-QUEST/MSP/Extra Help, aging/nutrition and housing; do not encode unverified thresholds.
- [ ] Retrieve the **DBEDT2024 self-sufficiency PDF**, tablesI.A/IV.A–E, to `data/raw/dbedt/self-sufficiency/2024/` for Q7’s budget context. It will not create an exact district hardship count.
- [ ] Retrieve **HUD FY 2026 Hawaiʻi income-limit rows** and applicable notices to `data/raw/programs/hud/income-limits/fy2026/`; select **FY 2027 FMR** data only if program rent benchmarks are needed, under `data/raw/hud/fmr/fy2027/`. Neither is a district median.
- [ ] Snapshot **HHFDC’s June 10,2026 inventory** into `data/raw/facilities/hhfdc/2026-06-10/`; verify locations/contacts before referrals. Store physical district assignment separately from service area and vacancy status.
- [ ] Acquire county polygons only for the documented county-intersection need, under `data/raw/geography/counties/`. Keep full county GEOIDs and CRS metadata.
- [ ] Select an exact **PEP/LAUS** release only for county/state trend questions; store `data/raw/population/pep/<vintage>/` and `data/raw/labor/laus/<release>/`. Retain native geographic scope and seasonal-adjustment status.
- [ ] Select **DHS Databook 2025 / Med-QUEST administrative attachments** for program context under `data/raw/administrative/<agency>/<release>/`. Review definitions/geographic detail before extracting counts.
- [ ] Schools/hospitals are optional concrete service-location features, under `data/raw/facilities/<type>/<date>/`. For education reports use [DOE Strive HI2024–25](https://hawaiipublicschools.org/sm/2025-strivehi2025/); report performance by school attended, not district residents. The [DHS childcare provider search](https://childcareprovidersearch.dhs.hawaii.gov/) can support future provider referrals; licensing is not vacancy data.

### H4. Advanced — acquire only with an approved analytical use case

- [ ] CHAS2018–2022: select table/geography/definitions from the official HUD catalog, retain disclosure rules, and decide whether native county context is enough before any district allocation.
- [ ] Tracts/BGs and Census relationship files: retrieve only the exact vintage/weights needed for a source lacking direct SLD estimates. Store native geometry in `data/raw/geography/` and versioned crosswalk inputs separately; do not reuse a generic area-only weight as validated demographic allocation.
- [ ] PUMS: retrieve documented person/housing files and replicate weights only for state/PUMA custom studies; no district estimates promised.
- [ ] BRFSS/PLACES: choose a specific public measure, release, native geography and uncertainty model. Exact release downloads remain **not selected/verified** in this study; the catalog links are official discovery entry points.
- [ ] Program participation: seek an existing public or agency-produced aggregate2022-SLD table with suppression and residency documentation; do not request resident-level records.
- [ ] District history: identify boundary-compatible ACS/decennial releases before downloading. Historical same-number districts can describe different areas. For genuinely comparable nonoverlapping ACS windows, 2015–2019 and2020–2024 are a possible temporal pairing only after geographic harmonization; raw district-ID joins are invalid across the2022 plan change.

## I. Recommended Implementation Roadmap

| Step | Work | Completion evidence |
| --- | --- | --- |
| 1 — Phase 2 reliability | Review existing raw row definitions/universes and register high-value measures; preserve existing APIs/evidence rendering | Database-backed education, SNAP receipt, disability, older-alone and child-household answers cite original cells/MOEs without any new import |
| 2 — Safe calculations | Add a small allowlist of sum/ratio/difference recipes with denominator and uncertainty rules; replace blanket cross-tab rejection with a capability check | Q6/8/9 calculations are reproducible; unsupported intersections reliably explain missing dimensions |
| 3 — First five tables | Fetch only Hawaiʻi SLD/county/state B17001/B25070/B25007/B25011/B19037 with metadata and annotations; idempotent imports through existing infrastructure | Exactly76 district IDs per applicable table; native values/MOEs match source; no existing row overwritten; new poverty counts and severe burden pass QA |
| 4 — Next five and dynamic discovery | Add B25008/S0103/S2201/B19058/B25106, then bounded metadata search/retrieval | Natural-language age/tenure/income/SNAP questions select the correct joint table and universe; no SQL tools or model-generated math |
| 5 — Broader comparisons and evaluation | Validate county intersections, same-chamber neighbors, geographic/period compatibility and uncertainty wording | All30 representative intents tested; unsupported answers are useful and accurate; current dashboard regression tests still pass |
| 6 — Phase 3 program information | Curate the initial official directory and current application status/rule versions; enable purpose/service-area search before eligibility screening | Cited program relevance for low-income older adults; closed HPHA waitlists and missing rule versions handled explicitly |
| 7 — Transparent screening, if requested | Encode fully verified rules with deterministic tests, unknown states and date selection; keep demographic need separate | Rule provenance, boundaries and effective periods are reviewable; no claim that ACS identifies eligible residents |
| 8 — Advanced sources selectively | Add administrative participation, geographic allocation, historical harmonization or document RAG only for demonstrated gaps | Each new capability has a specific use case, methodology, quality review and explicit native-versus-modeled label |

A reasonable hackathon scope is steps1–5 plus a small verified program-information directory, with no mass data lake, no mandatory vector database and no tract allocation for tables already available by district.

### Acceptance checks for the next implementation, not claims of work completed here

- Existing46 aliases, 76 district polygons, 82 statistical geographies and historical source files remain intact.
- Raw-measure metadata identifies count/percent/median roles and universes, including repeated total/section labels.
- Sample rows in House 30, another House district, a Senate district, a county and statewide match native estimates, MOEs and annotations.
- B17001 subgroup counts reconcile with its own universes; B25070 not-computed/no-cash-rent distinctions are preserved.
- Native Census IDs match the correct chamber and2022 plan; missing/suppressed district cells are flagged rather than silently dropped.
- The assistant retrieves facts in the current turn, never invents a compound intersection, and correctly distinguishes age 60+,65+,householder versus person, and poverty versus program income guidelines.
- Comparisons distinguish whole county from county remainder and do not subtract medians or declare significance without a valid method.
- Program cards cite effective rules and application status; unavailable rules block eligibility claims while allowing informational referral.
- Existing backend/frontend tests, integration checks and browser flows are rerun **when implementation changes occur**. This research did not rerun or re-certify the prior Phase 2 test suite.

## J. Executive Recommendation

**The first improvement should be exposing the valuable data already imported.** Education, household children, grandparents, older-adult poverty rates, disability, broadband and benefit-receipt measures do not require another download. This is the fastest way to broaden Phase 2 coverage while preserving trust.

Then acquire these ten official2024 ACS five-year tables, in this order:

1. **B17001** — older/child poverty counts and matched universes; broad direct benefit to common constituent questions.
2. **B25070** — severe renter burden at50%+, currently impossible to separate from35%+.
3. **B25007** — ownership/renting for households headed by older adults.
4. **B25011** — genuine older-alone-by-tenure combinations.
5. **B19037** — household income by householder age.
6. **B25008** — residents’ tenure rather than household tenure.
7. **S0103** — a coherent65+ profile and appropriately labeled older-householder income-source context.
8. **S2201** — SNAP household characteristics and genuine receipt cross-tabulations.
9. **B19058** — a defined assistance-or-SNAP union without double-counting.
10. **B25106** — income × housing burden × tenure, after completing metadata/coverage QA.

All are selected for useful published combinations and low geographic engineering cost, rather than maximum dataset volume. Start with the first five and verify them before adding the rest. Build the initial official program directory alongside this statistical work only after Phase 2 retrieval is reliable; keep unknown eligibility rules unknown. Defer PUMS, CHAS allocation, health modeling and RAG until a concrete question justifies them.

### Deliverables and research evidence

- `DistrictIQ-Data-Requirements-and-Acquisition-Report.md` — this integrated A–J report.
- `existing-data-inventory.md` — all 46 mapped definitions and542 preserved worksheet row definitions, with actual availability counts.
- `question-to-data-matrix.md` and `.json` — all 30 questions, universes, sources, availability and limitations.
- `dataset-catalog.md` and `.json` — exact selected statistical tables and official source discovery records, priorities, verification notes and proposed storage.
- `program-information-catalog.md` and `.json` —16 initial program/directory records, application/referral sources, effective-date/status findings and outstanding rule verification.
- `work/data-study/database-audit.json` — read-only local database audit evidence.
- `work/data-study/census-table-verification.json` — bounded metadata request outcomes; a successful metadata request is not a successful district data import.

**Remaining verification before acquisition/implementation:** activate a Census data-query key or use manualCSV exports; validate each selected table’s76-district coverage and native annotations; resolve timed-out metadata/cell checks; obtain blocked Med-QUEST thresholds; confirm current local program rules, capacity and FY 2027 energy-assistance details; select exact optional administrative/health/historical files only when needed. No source listed as unverified or not selected should become production evidence by implication.
