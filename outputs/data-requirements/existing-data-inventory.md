# DistrictIQ existing-data inventory appendix

Audit date: 2026-10-26 (Hawaiʻi time). Source: live read-only PostgreSQL audit plus repository inspection. This is an inventory, not a new import. All row references below are **physical Excel worksheet row numbers**, not inferred Census API variable codes. The source workbook hash, geographic label, cells, reported strings and period are preserved in PostgreSQL.

## Mapped dashboard / assistant fields

46 registered fields, 44 numeric values per geography and two explicitly unavailable poverty count/universe fields. Distribution members are fields; they are not 46 separate statistical topics.

| Code | Label | Unit | Workbook location | Measure |
| --- | --- | --- | --- | --- |
| population | Total population | people | DP05 row 4 | estimate |
| median_age | Median age (years) | years | DP05 row 21 | estimate |
| age_under_18 | Under 18 years | people | DP05 row 22 | estimate |
| age_65_plus | 65 years and over | people | DP05 row 27 | estimate |
| older_adult_share | 65 years and over | percent | DP05 row 27 | percent |
| median_household_income | Median household income (dollars) | USD | DP03 row 70 | estimate |
| per_capita_income | Per capita income (dollars) | USD | DP03 row 96 | estimate |
| poverty_rate | All people whose income in the past 12 months is below the poverty level | percent | DP03 row 138 | percent |
| poverty_population | People below poverty (count not published in supplied profile) | people | DP03 row 138 | estimate |
| households | Total households | households | DP02 row 4 | estimate |
| total_housing_units | Total housing units | housing units | DP04 row 4 | estimate |
| owner_occupied | Owner-occupied | households | DP04 row 54 | estimate |
| renter_occupied | Renter-occupied | households | DP04 row 55 | estimate |
| median_gross_rent | Median gross rent (dollars) | USD | DP04 row 152 | estimate |
| age_profile_01 | Under 5 years | people | DP05 row 8 | estimate |
| age_profile_02 | 5 to 9 years | people | DP05 row 9 | estimate |
| age_profile_03 | 10 to 14 years | people | DP05 row 10 | estimate |
| age_profile_04 | 15 to 19 years | people | DP05 row 11 | estimate |
| age_profile_05 | 20 to 24 years | people | DP05 row 12 | estimate |
| age_profile_06 | 25 to 34 years | people | DP05 row 13 | estimate |
| age_profile_07 | 35 to 44 years | people | DP05 row 14 | estimate |
| age_profile_08 | 45 to 54 years | people | DP05 row 15 | estimate |
| age_profile_09 | 55 to 59 years | people | DP05 row 16 | estimate |
| age_profile_10 | 60 to 64 years | people | DP05 row 17 | estimate |
| age_profile_11 | 65 to 74 years | people | DP05 row 18 | estimate |
| age_profile_12 | 75 to 84 years | people | DP05 row 19 | estimate |
| age_profile_13 | 85 years and over | people | DP05 row 20 | estimate |
| income_profile_01 | Less than $10,000 | households | DP03 row 60 | estimate |
| income_profile_02 | $10,000 to $14,999 | households | DP03 row 61 | estimate |
| income_profile_03 | $15,000 to $24,999 | households | DP03 row 62 | estimate |
| income_profile_04 | $25,000 to $34,999 | households | DP03 row 63 | estimate |
| income_profile_05 | $35,000 to $49,999 | households | DP03 row 64 | estimate |
| income_profile_06 | $50,000 to $74,999 | households | DP03 row 65 | estimate |
| income_profile_07 | $75,000 to $99,999 | households | DP03 row 66 | estimate |
| income_profile_08 | $100,000 to $149,999 | households | DP03 row 67 | estimate |
| income_profile_09 | $150,000 to $199,999 | households | DP03 row 68 | estimate |
| income_profile_10 | $200,000 or more | households | DP03 row 69 | estimate |
| rent_burden_denominator | Rent burden universe | households | DP04 row 155 | estimate |
| rent_burden_30_34 | Rent: 30–34.9% of household income | households | DP04 row 160 | estimate |
| rent_burden_35_plus | Rent: 35% or more of household income | households | DP04 row 161 | estimate |
| mortgage_burden_denominator | Mortgage owner-cost universe | households | DP04 row 127 | estimate |
| mortgage_burden_30_34 | Mortgaged owner costs: 30–34.9% | households | DP04 row 131 | estimate |
| mortgage_burden_35_plus | Mortgaged owner costs: 35% or more | households | DP04 row 132 | estimate |
| unmortgaged_burden_30_34 | Unmortgaged owner costs: 30–34.9% | households | DP04 row 140 | estimate |
| unmortgaged_burden_35_plus | Unmortgaged owner costs: 35% or more | households | DP04 row 141 | estimate |
| poverty_denominator | Population with poverty status determined (not published in supplied profile) | people | DP03 row 138 | unavailable |

## All 542 preserved row definitions

Each row is represented for all 82 geographies. Numeric availability counts below refer to estimate and percent columns independently. A cell in the workbook’s percent column is **not always a percentage**: total-universe values can repeat the count, while median/mean rows may have `(X)`. Hierarchical context, statistical universe and measure role must be curated before exposing a row through the assistant. Null numeric values retain the original published marker and must not become zero.

| Profile | Excel row | Section | Definition | Geographies | Numeric estimates | Numeric percent-column cells |
| --- | --- | --- | --- | --- | --- | --- |
| DP02 | 4 | HOUSEHOLDS BY TYPE | Total households | 82 | 82 | 82 |
| DP02 | 5 | HOUSEHOLDS BY TYPE | Married-couple household | 82 | 82 | 82 |
| DP02 | 6 | HOUSEHOLDS BY TYPE | With children of the householder under 18 years | 82 | 82 | 82 |
| DP02 | 7 | HOUSEHOLDS BY TYPE | Cohabiting couple household | 82 | 82 | 82 |
| DP02 | 8 | HOUSEHOLDS BY TYPE | With children of the householder under 18 years | 82 | 82 | 82 |
| DP02 | 9 | HOUSEHOLDS BY TYPE | Male householder, no spouse/partner present | 82 | 82 | 82 |
| DP02 | 10 | HOUSEHOLDS BY TYPE | With children of the householder under 18 years | 82 | 82 | 82 |
| DP02 | 11 | HOUSEHOLDS BY TYPE | Householder living alone | 82 | 82 | 82 |
| DP02 | 12 | HOUSEHOLDS BY TYPE | 65 years and over | 82 | 82 | 82 |
| DP02 | 13 | HOUSEHOLDS BY TYPE | Female householder, no spouse/partner present | 82 | 82 | 82 |
| DP02 | 14 | HOUSEHOLDS BY TYPE | With children of the householder under 18 years | 82 | 82 | 82 |
| DP02 | 15 | HOUSEHOLDS BY TYPE | Householder living alone | 82 | 82 | 82 |
| DP02 | 16 | HOUSEHOLDS BY TYPE | 65 years and over | 82 | 82 | 82 |
| DP02 | 17 | HOUSEHOLDS BY TYPE | Households with one or more people under 18 years | 82 | 82 | 82 |
| DP02 | 18 | HOUSEHOLDS BY TYPE | Households with one or more people 65 years and over | 82 | 82 | 82 |
| DP02 | 19 | HOUSEHOLDS BY TYPE | Average household size | 82 | 82 | 0 |
| DP02 | 20 | HOUSEHOLDS BY TYPE | Average family size | 82 | 82 | 0 |
| DP02 | 22 | RELATIONSHIP | Population in households | 82 | 82 | 82 |
| DP02 | 23 | RELATIONSHIP | Householder | 82 | 82 | 82 |
| DP02 | 24 | RELATIONSHIP | Spouse | 82 | 82 | 82 |
| DP02 | 25 | RELATIONSHIP | Unmarried partner | 82 | 82 | 82 |
| DP02 | 26 | RELATIONSHIP | Child | 82 | 82 | 82 |
| DP02 | 27 | RELATIONSHIP | Other relatives | 82 | 82 | 82 |
| DP02 | 28 | RELATIONSHIP | Other nonrelatives | 82 | 82 | 82 |
| DP02 | 30 | MARITAL STATUS | Males 15 years and over | 82 | 82 | 82 |
| DP02 | 31 | MARITAL STATUS | Never married | 82 | 82 | 82 |
| DP02 | 32 | MARITAL STATUS | Now married, except separated | 82 | 82 | 82 |
| DP02 | 33 | MARITAL STATUS | Separated | 82 | 82 | 82 |
| DP02 | 34 | MARITAL STATUS | Widowed | 82 | 82 | 82 |
| DP02 | 35 | MARITAL STATUS | Divorced | 82 | 82 | 82 |
| DP02 | 36 | MARITAL STATUS | Females 15 years and over | 82 | 82 | 82 |
| DP02 | 37 | MARITAL STATUS | Never married | 82 | 82 | 82 |
| DP02 | 38 | MARITAL STATUS | Now married, except separated | 82 | 82 | 82 |
| DP02 | 39 | MARITAL STATUS | Separated | 82 | 82 | 82 |
| DP02 | 40 | MARITAL STATUS | Widowed | 82 | 82 | 82 |
| DP02 | 41 | MARITAL STATUS | Divorced | 82 | 82 | 82 |
| DP02 | 43 | FERTILITY | Number of women 15 to 50 years old who had a birth in the past 12 months | 82 | 82 | 82 |
| DP02 | 44 | FERTILITY | Unmarried women (widowed, divorced, and never married) | 82 | 82 | 81 |
| DP02 | 45 | FERTILITY | Per 1,000 unmarried women | 82 | 82 | 0 |
| DP02 | 46 | FERTILITY | Per 1,000 women 15 to 50 years old | 82 | 82 | 0 |
| DP02 | 47 | FERTILITY | Per 1,000 women 15 to 19 years old | 82 | 81 | 0 |
| DP02 | 48 | FERTILITY | Per 1,000 women 20 to 34 years old | 82 | 81 | 0 |
| DP02 | 49 | FERTILITY | Per 1,000 women 35 to 50 years old | 82 | 82 | 0 |
| DP02 | 51 | GRANDPARENTS | Number of grandparents living with own grandchildren under 18 years | 82 | 82 | 82 |
| DP02 | 52 | GRANDPARENTS | Grandparents responsible for grandchildren | 82 | 82 | 81 |
| DP02 | 54 | Years responsible for grandchildren | Less than 1 year | 82 | 82 | 81 |
| DP02 | 55 | Years responsible for grandchildren | 1 or 2 years | 82 | 82 | 81 |
| DP02 | 56 | Years responsible for grandchildren | 3 or 4 years | 82 | 82 | 81 |
| DP02 | 57 | Years responsible for grandchildren | 5 or more years | 82 | 82 | 81 |
| DP02 | 58 | Years responsible for grandchildren | Number of grandparents responsible for own grandchildren under 18 years | 82 | 82 | 82 |
| DP02 | 59 | Years responsible for grandchildren | Who are female | 82 | 82 | 81 |
| DP02 | 60 | Years responsible for grandchildren | Who are married | 82 | 82 | 81 |
| DP02 | 62 | SCHOOL ENROLLMENT | Population 3 years and over enrolled in school | 82 | 82 | 82 |
| DP02 | 63 | SCHOOL ENROLLMENT | Nursery school, preschool | 82 | 82 | 81 |
| DP02 | 64 | SCHOOL ENROLLMENT | Kindergarten | 82 | 82 | 81 |
| DP02 | 65 | SCHOOL ENROLLMENT | Elementary school (grades 1-8) | 82 | 82 | 81 |
| DP02 | 66 | SCHOOL ENROLLMENT | High school (grades 9-12) | 82 | 82 | 81 |
| DP02 | 67 | SCHOOL ENROLLMENT | College or graduate school | 82 | 82 | 81 |
| DP02 | 69 | EDUCATIONAL ATTAINMENT | Population 25 years and over | 82 | 82 | 82 |
| DP02 | 70 | EDUCATIONAL ATTAINMENT | Less than 9th grade | 82 | 82 | 82 |
| DP02 | 71 | EDUCATIONAL ATTAINMENT | 9th to 12th grade, no diploma | 82 | 82 | 82 |
| DP02 | 72 | EDUCATIONAL ATTAINMENT | High school graduate (includes equivalency) | 82 | 82 | 82 |
| DP02 | 73 | EDUCATIONAL ATTAINMENT | Some college, no degree | 82 | 82 | 82 |
| DP02 | 74 | EDUCATIONAL ATTAINMENT | Associate's degree | 82 | 82 | 82 |
| DP02 | 75 | EDUCATIONAL ATTAINMENT | Bachelor's degree | 82 | 82 | 82 |
| DP02 | 76 | EDUCATIONAL ATTAINMENT | Graduate or professional degree | 82 | 82 | 82 |
| DP02 | 77 | EDUCATIONAL ATTAINMENT | High school graduate or higher | 82 | 82 | 82 |
| DP02 | 78 | EDUCATIONAL ATTAINMENT | Bachelor's degree or higher | 82 | 82 | 82 |
| DP02 | 80 | VETERAN STATUS | Civilian population 18 years and over | 82 | 82 | 82 |
| DP02 | 81 | VETERAN STATUS | Civilian veterans | 82 | 82 | 82 |
| DP02 | 83 | DISABILITY STATUS OF THE CIVILIAN NONINSTITUTIONALIZED POPULATION | Total Civilian Noninstitutionalized Population | 82 | 82 | 82 |
| DP02 | 84 | DISABILITY STATUS OF THE CIVILIAN NONINSTITUTIONALIZED POPULATION | With a disability | 82 | 82 | 82 |
| DP02 | 85 | DISABILITY STATUS OF THE CIVILIAN NONINSTITUTIONALIZED POPULATION | Under 18 years | 82 | 82 | 82 |
| DP02 | 86 | DISABILITY STATUS OF THE CIVILIAN NONINSTITUTIONALIZED POPULATION | With a disability | 82 | 82 | 81 |
| DP02 | 87 | DISABILITY STATUS OF THE CIVILIAN NONINSTITUTIONALIZED POPULATION | 18 to 64 years | 82 | 82 | 82 |
| DP02 | 88 | DISABILITY STATUS OF THE CIVILIAN NONINSTITUTIONALIZED POPULATION | With a disability | 82 | 82 | 82 |
| DP02 | 89 | DISABILITY STATUS OF THE CIVILIAN NONINSTITUTIONALIZED POPULATION | 65 years and over | 82 | 82 | 82 |
| DP02 | 90 | DISABILITY STATUS OF THE CIVILIAN NONINSTITUTIONALIZED POPULATION | With a disability | 82 | 82 | 82 |
| DP02 | 92 | RESIDENCE 1 YEAR AGO | Population 1 year and over | 82 | 82 | 82 |
| DP02 | 93 | RESIDENCE 1 YEAR AGO | Same house | 82 | 82 | 82 |
| DP02 | 94 | RESIDENCE 1 YEAR AGO | Different house (in the U.S. or abroad) | 82 | 82 | 82 |
| DP02 | 95 | RESIDENCE 1 YEAR AGO | Different house in the U.S. | 82 | 82 | 82 |
| DP02 | 96 | RESIDENCE 1 YEAR AGO | Same county | 82 | 82 | 82 |
| DP02 | 97 | RESIDENCE 1 YEAR AGO | Different county | 82 | 82 | 82 |
| DP02 | 98 | RESIDENCE 1 YEAR AGO | Same state | 82 | 82 | 82 |
| DP02 | 99 | RESIDENCE 1 YEAR AGO | Different state | 82 | 82 | 82 |
| DP02 | 100 | RESIDENCE 1 YEAR AGO | Abroad | 82 | 82 | 82 |
| DP02 | 102 | PLACE OF BIRTH | Total population | 82 | 82 | 82 |
| DP02 | 103 | PLACE OF BIRTH | Native | 82 | 82 | 82 |
| DP02 | 104 | PLACE OF BIRTH | Born in United States | 82 | 82 | 82 |
| DP02 | 105 | PLACE OF BIRTH | State of residence | 82 | 82 | 82 |
| DP02 | 106 | PLACE OF BIRTH | Different state | 82 | 82 | 82 |
| DP02 | 107 | PLACE OF BIRTH | Born in Puerto Rico, U.S. Island areas, or born abroad to American parent(s) | 82 | 82 | 82 |
| DP02 | 108 | PLACE OF BIRTH | Foreign-born | 82 | 82 | 82 |
| DP02 | 110 | U.S. CITIZENSHIP STATUS | Foreign-born population | 82 | 82 | 82 |
| DP02 | 111 | U.S. CITIZENSHIP STATUS | Naturalized U.S. citizen | 82 | 82 | 82 |
| DP02 | 112 | U.S. CITIZENSHIP STATUS | Not a U.S. citizen | 82 | 82 | 82 |
| DP02 | 114 | YEAR OF ENTRY | Population born outside the United States | 82 | 82 | 82 |
| DP02 | 115 | YEAR OF ENTRY | Native | 82 | 82 | 82 |
| DP02 | 116 | YEAR OF ENTRY | Entered 2010 or later | 82 | 82 | 81 |
| DP02 | 117 | YEAR OF ENTRY | Entered before 2010 | 82 | 82 | 81 |
| DP02 | 118 | YEAR OF ENTRY | Foreign-born | 82 | 82 | 82 |
| DP02 | 119 | YEAR OF ENTRY | Entered 2010 or later | 82 | 82 | 82 |
| DP02 | 120 | YEAR OF ENTRY | Entered before 2010 | 82 | 82 | 82 |
| DP02 | 122 | WORLD REGION OF BIRTH OF FOREIGN-BORN | Foreign-born population, excluding population born at sea | 82 | 82 | 82 |
| DP02 | 123 | WORLD REGION OF BIRTH OF FOREIGN-BORN | Europe | 82 | 82 | 82 |
| DP02 | 124 | WORLD REGION OF BIRTH OF FOREIGN-BORN | Asia | 82 | 82 | 82 |
| DP02 | 125 | WORLD REGION OF BIRTH OF FOREIGN-BORN | Africa | 82 | 82 | 82 |
| DP02 | 126 | WORLD REGION OF BIRTH OF FOREIGN-BORN | Oceania | 82 | 82 | 82 |
| DP02 | 127 | WORLD REGION OF BIRTH OF FOREIGN-BORN | Latin America | 82 | 82 | 82 |
| DP02 | 128 | WORLD REGION OF BIRTH OF FOREIGN-BORN | Northern America | 82 | 82 | 82 |
| DP02 | 130 | LANGUAGE SPOKEN AT HOME | Population 5 years and over | 82 | 82 | 82 |
| DP02 | 131 | LANGUAGE SPOKEN AT HOME | English only | 82 | 82 | 82 |
| DP02 | 132 | LANGUAGE SPOKEN AT HOME | Language other than English | 82 | 82 | 82 |
| DP02 | 133 | LANGUAGE SPOKEN AT HOME | Speak English less than "very well" | 82 | 82 | 82 |
| DP02 | 134 | LANGUAGE SPOKEN AT HOME | Spanish | 82 | 82 | 82 |
| DP02 | 135 | LANGUAGE SPOKEN AT HOME | Speak English less than "very well" | 82 | 82 | 82 |
| DP02 | 136 | LANGUAGE SPOKEN AT HOME | Other Indo-European languages | 82 | 82 | 82 |
| DP02 | 137 | LANGUAGE SPOKEN AT HOME | Speak English less than "very well" | 82 | 82 | 82 |
| DP02 | 138 | LANGUAGE SPOKEN AT HOME | Asian and Pacific Islander languages | 82 | 82 | 82 |
| DP02 | 139 | LANGUAGE SPOKEN AT HOME | Speak English less than "very well" | 82 | 82 | 82 |
| DP02 | 140 | LANGUAGE SPOKEN AT HOME | Other languages | 82 | 82 | 82 |
| DP02 | 141 | LANGUAGE SPOKEN AT HOME | Speak English less than "very well" | 82 | 82 | 82 |
| DP02 | 143 | ANCESTRY | Total population | 82 | 82 | 82 |
| DP02 | 144 | ANCESTRY | American | 82 | 82 | 82 |
| DP02 | 145 | ANCESTRY | Arab | 82 | 82 | 82 |
| DP02 | 146 | ANCESTRY | Czech | 82 | 82 | 82 |
| DP02 | 147 | ANCESTRY | Danish | 82 | 82 | 82 |
| DP02 | 148 | ANCESTRY | Dutch | 82 | 82 | 82 |
| DP02 | 149 | ANCESTRY | English | 82 | 82 | 82 |
| DP02 | 150 | ANCESTRY | French (except Basque) | 82 | 82 | 82 |
| DP02 | 151 | ANCESTRY | French Canadian | 82 | 82 | 82 |
| DP02 | 152 | ANCESTRY | German | 82 | 82 | 82 |
| DP02 | 153 | ANCESTRY | Greek | 82 | 82 | 82 |
| DP02 | 154 | ANCESTRY | Hungarian | 82 | 82 | 82 |
| DP02 | 155 | ANCESTRY | Irish | 82 | 82 | 82 |
| DP02 | 156 | ANCESTRY | Italian | 82 | 82 | 82 |
| DP02 | 157 | ANCESTRY | Lithuanian | 82 | 82 | 82 |
| DP02 | 158 | ANCESTRY | Norwegian | 82 | 82 | 82 |
| DP02 | 159 | ANCESTRY | Polish | 82 | 82 | 82 |
| DP02 | 160 | ANCESTRY | Portuguese | 82 | 82 | 82 |
| DP02 | 161 | ANCESTRY | Russian | 82 | 82 | 82 |
| DP02 | 162 | ANCESTRY | Scotch-Irish | 82 | 82 | 82 |
| DP02 | 163 | ANCESTRY | Scottish | 82 | 82 | 82 |
| DP02 | 164 | ANCESTRY | Slovak | 82 | 82 | 82 |
| DP02 | 165 | ANCESTRY | Subsaharan African | 82 | 82 | 82 |
| DP02 | 166 | ANCESTRY | Swedish | 82 | 82 | 82 |
| DP02 | 167 | ANCESTRY | Swiss | 82 | 82 | 82 |
| DP02 | 168 | ANCESTRY | Ukrainian | 82 | 82 | 82 |
| DP02 | 169 | ANCESTRY | Welsh | 82 | 82 | 82 |
| DP02 | 170 | ANCESTRY | West Indian (excluding Hispanic origin groups) | 82 | 82 | 82 |
| DP02 | 172 | COMPUTERS AND INTERNET USE | Total households | 82 | 82 | 82 |
| DP02 | 173 | COMPUTERS AND INTERNET USE | With a computer | 82 | 82 | 82 |
| DP02 | 174 | COMPUTERS AND INTERNET USE | With a broadband Internet subscription | 82 | 82 | 82 |
| DP03 | 4 | EMPLOYMENT STATUS | Population 16 years and over | 82 | 82 | 82 |
| DP03 | 5 | EMPLOYMENT STATUS | In labor force | 82 | 82 | 82 |
| DP03 | 6 | EMPLOYMENT STATUS | Civilian labor force | 82 | 82 | 82 |
| DP03 | 7 | EMPLOYMENT STATUS | Employed | 82 | 82 | 82 |
| DP03 | 8 | EMPLOYMENT STATUS | Unemployed | 82 | 82 | 82 |
| DP03 | 9 | EMPLOYMENT STATUS | Armed Forces | 82 | 82 | 82 |
| DP03 | 10 | EMPLOYMENT STATUS | Not in labor force | 82 | 82 | 82 |
| DP03 | 11 | EMPLOYMENT STATUS | Civilian labor force | 82 | 82 | 82 |
| DP03 | 12 | EMPLOYMENT STATUS | Unemployment Rate | 82 | 0 | 82 |
| DP03 | 13 | EMPLOYMENT STATUS | Females 16 years and over | 82 | 82 | 82 |
| DP03 | 14 | EMPLOYMENT STATUS | In labor force | 82 | 82 | 82 |
| DP03 | 15 | EMPLOYMENT STATUS | Civilian labor force | 82 | 82 | 82 |
| DP03 | 16 | EMPLOYMENT STATUS | Employed | 82 | 82 | 82 |
| DP03 | 17 | EMPLOYMENT STATUS | Own children of the householder under 6 years | 82 | 82 | 82 |
| DP03 | 18 | EMPLOYMENT STATUS | All parents in family in labor force | 82 | 82 | 81 |
| DP03 | 19 | EMPLOYMENT STATUS | Own children of the householder 6 to 17 years | 82 | 82 | 82 |
| DP03 | 20 | EMPLOYMENT STATUS | All parents in family in labor force | 82 | 82 | 81 |
| DP03 | 22 | COMMUTING TO WORK | Workers 16 years and over | 82 | 82 | 82 |
| DP03 | 23 | COMMUTING TO WORK | Car, truck, or van -- drove alone | 82 | 82 | 82 |
| DP03 | 24 | COMMUTING TO WORK | Car, truck, or van -- carpooled | 82 | 82 | 82 |
| DP03 | 25 | COMMUTING TO WORK | Public transportation | 82 | 82 | 82 |
| DP03 | 26 | COMMUTING TO WORK | Walked | 82 | 82 | 82 |
| DP03 | 27 | COMMUTING TO WORK | Other means | 82 | 82 | 82 |
| DP03 | 28 | COMMUTING TO WORK | Worked from home | 82 | 82 | 82 |
| DP03 | 29 | COMMUTING TO WORK | Mean travel time to work (minutes) | 82 | 82 | 0 |
| DP03 | 31 | OCCUPATION | Civilian employed population 16 years and over | 82 | 82 | 82 |
| DP03 | 32 | OCCUPATION | Management, business, science, and arts occupations | 82 | 82 | 82 |
| DP03 | 33 | OCCUPATION | Service occupations | 82 | 82 | 82 |
| DP03 | 34 | OCCUPATION | Sales and office occupations | 82 | 82 | 82 |
| DP03 | 35 | OCCUPATION | Natural resources, construction, and maintenance occupations | 82 | 82 | 82 |
| DP03 | 36 | OCCUPATION | Production, transportation, and material moving occupations | 82 | 82 | 82 |
| DP03 | 38 | INDUSTRY | Civilian employed population 16 years and over | 82 | 82 | 82 |
| DP03 | 39 | INDUSTRY | Agriculture, forestry, fishing and hunting, and mining | 82 | 82 | 82 |
| DP03 | 40 | INDUSTRY | Construction | 82 | 82 | 82 |
| DP03 | 41 | INDUSTRY | Manufacturing | 82 | 82 | 82 |
| DP03 | 42 | INDUSTRY | Wholesale trade | 82 | 82 | 82 |
| DP03 | 43 | INDUSTRY | Retail trade | 82 | 82 | 82 |
| DP03 | 44 | INDUSTRY | Transportation and warehousing, and utilities | 82 | 82 | 82 |
| DP03 | 45 | INDUSTRY | Information | 82 | 82 | 82 |
| DP03 | 46 | INDUSTRY | Finance and insurance, and real estate and rental and leasing | 82 | 82 | 82 |
| DP03 | 47 | INDUSTRY | Professional, scientific, and management, and administrative and waste management services | 82 | 82 | 82 |
| DP03 | 48 | INDUSTRY | Educational services, and health care and social assistance | 82 | 82 | 82 |
| DP03 | 49 | INDUSTRY | Arts, entertainment, and recreation, and accommodation and food services | 82 | 82 | 82 |
| DP03 | 50 | INDUSTRY | Other services, except public administration | 82 | 82 | 82 |
| DP03 | 51 | INDUSTRY | Public administration | 82 | 82 | 82 |
| DP03 | 53 | CLASS OF WORKER | Civilian employed population 16 years and over | 82 | 82 | 82 |
| DP03 | 54 | CLASS OF WORKER | Private wage and salary workers | 82 | 82 | 82 |
| DP03 | 55 | CLASS OF WORKER | Government workers | 82 | 82 | 82 |
| DP03 | 56 | CLASS OF WORKER | Self-employed in own not incorporated business workers | 82 | 82 | 82 |
| DP03 | 57 | CLASS OF WORKER | Unpaid family workers | 82 | 82 | 82 |
| DP03 | 59 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Total households | 82 | 82 | 82 |
| DP03 | 60 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Less than $10,000 | 82 | 82 | 82 |
| DP03 | 61 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $10,000 to $14,999 | 82 | 82 | 82 |
| DP03 | 62 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $15,000 to $24,999 | 82 | 82 | 82 |
| DP03 | 63 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $25,000 to $34,999 | 82 | 82 | 82 |
| DP03 | 64 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $35,000 to $49,999 | 82 | 82 | 82 |
| DP03 | 65 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $50,000 to $74,999 | 82 | 82 | 82 |
| DP03 | 66 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $75,000 to $99,999 | 82 | 82 | 82 |
| DP03 | 67 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $100,000 to $149,999 | 82 | 82 | 82 |
| DP03 | 68 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $150,000 to $199,999 | 82 | 82 | 82 |
| DP03 | 69 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $200,000 or more | 82 | 82 | 82 |
| DP03 | 70 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Median household income (dollars) | 82 | 82 | 0 |
| DP03 | 71 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Mean household income (dollars) | 82 | 82 | 0 |
| DP03 | 72 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | With earnings | 82 | 82 | 82 |
| DP03 | 73 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Mean earnings (dollars) | 82 | 82 | 0 |
| DP03 | 74 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | With Social Security | 82 | 82 | 82 |
| DP03 | 75 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Mean Social Security income (dollars) | 82 | 82 | 0 |
| DP03 | 76 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | With retirement income | 82 | 82 | 82 |
| DP03 | 77 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Mean retirement income (dollars) | 82 | 82 | 0 |
| DP03 | 78 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | With Supplemental Security Income | 82 | 82 | 82 |
| DP03 | 79 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Mean Supplemental Security Income (dollars) | 82 | 81 | 0 |
| DP03 | 80 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | With cash public assistance income | 82 | 82 | 82 |
| DP03 | 81 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Mean cash public assistance income (dollars) | 82 | 81 | 0 |
| DP03 | 82 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | With Food Stamp/SNAP benefits in the past 12 months | 82 | 82 | 82 |
| DP03 | 83 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Families | 82 | 82 | 82 |
| DP03 | 84 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Less than $10,000 | 82 | 82 | 82 |
| DP03 | 85 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $10,000 to $14,999 | 82 | 82 | 82 |
| DP03 | 86 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $15,000 to $24,999 | 82 | 82 | 82 |
| DP03 | 87 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $25,000 to $34,999 | 82 | 82 | 82 |
| DP03 | 88 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $35,000 to $49,999 | 82 | 82 | 82 |
| DP03 | 89 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $50,000 to $74,999 | 82 | 82 | 82 |
| DP03 | 90 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $75,000 to $99,999 | 82 | 82 | 82 |
| DP03 | 91 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $100,000 to $149,999 | 82 | 82 | 82 |
| DP03 | 92 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $150,000 to $199,999 | 82 | 82 | 82 |
| DP03 | 93 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | $200,000 or more | 82 | 82 | 82 |
| DP03 | 94 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Median family income (dollars) | 82 | 81 | 0 |
| DP03 | 95 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Mean family income (dollars) | 82 | 81 | 0 |
| DP03 | 96 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Per capita income (dollars) | 82 | 82 | 0 |
| DP03 | 97 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Nonfamily households | 82 | 82 | 82 |
| DP03 | 98 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Median nonfamily income (dollars) | 82 | 82 | 0 |
| DP03 | 99 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Mean nonfamily income (dollars) | 82 | 82 | 0 |
| DP03 | 100 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Median earnings for workers (dollars) | 82 | 82 | 0 |
| DP03 | 101 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Median earnings for male full-time, year-round workers (dollars) | 82 | 82 | 0 |
| DP03 | 102 | INCOME AND BENEFITS (IN 2024 INFLATION-ADJUSTED DOLLARS) | Median earnings for female full-time, year-round workers (dollars) | 82 | 82 | 0 |
| DP03 | 104 | HEALTH INSURANCE COVERAGE | Civilian noninstitutionalized population | 82 | 82 | 82 |
| DP03 | 105 | HEALTH INSURANCE COVERAGE | With health insurance coverage | 82 | 82 | 82 |
| DP03 | 106 | HEALTH INSURANCE COVERAGE | With private health insurance | 82 | 82 | 82 |
| DP03 | 107 | HEALTH INSURANCE COVERAGE | With public coverage | 82 | 82 | 82 |
| DP03 | 108 | HEALTH INSURANCE COVERAGE | No health insurance coverage | 82 | 82 | 82 |
| DP03 | 109 | HEALTH INSURANCE COVERAGE | Civilian noninstitutionalized population under 19 years | 82 | 82 | 82 |
| DP03 | 110 | HEALTH INSURANCE COVERAGE | No health insurance coverage | 82 | 82 | 81 |
| DP03 | 111 | HEALTH INSURANCE COVERAGE | Civilian noninstitutionalized population 19 to 64 years | 82 | 82 | 82 |
| DP03 | 112 | HEALTH INSURANCE COVERAGE | In labor force: | 82 | 82 | 82 |
| DP03 | 113 | HEALTH INSURANCE COVERAGE | Employed: | 82 | 82 | 82 |
| DP03 | 114 | HEALTH INSURANCE COVERAGE | With health insurance coverage | 82 | 82 | 82 |
| DP03 | 115 | HEALTH INSURANCE COVERAGE | With private health insurance | 82 | 82 | 82 |
| DP03 | 116 | HEALTH INSURANCE COVERAGE | With public coverage | 82 | 82 | 82 |
| DP03 | 117 | HEALTH INSURANCE COVERAGE | No health insurance coverage | 82 | 82 | 82 |
| DP03 | 118 | HEALTH INSURANCE COVERAGE | Unemployed: | 82 | 82 | 82 |
| DP03 | 119 | HEALTH INSURANCE COVERAGE | With health insurance coverage | 82 | 82 | 81 |
| DP03 | 120 | HEALTH INSURANCE COVERAGE | With private health insurance | 82 | 82 | 81 |
| DP03 | 121 | HEALTH INSURANCE COVERAGE | With public coverage | 82 | 82 | 81 |
| DP03 | 122 | HEALTH INSURANCE COVERAGE | No health insurance coverage | 82 | 82 | 81 |
| DP03 | 123 | HEALTH INSURANCE COVERAGE | Not in labor force: | 82 | 82 | 82 |
| DP03 | 124 | HEALTH INSURANCE COVERAGE | With health insurance coverage | 82 | 82 | 82 |
| DP03 | 125 | HEALTH INSURANCE COVERAGE | With private health insurance | 82 | 82 | 82 |
| DP03 | 126 | HEALTH INSURANCE COVERAGE | With public coverage | 82 | 82 | 82 |
| DP03 | 127 | HEALTH INSURANCE COVERAGE | No health insurance coverage | 82 | 82 | 82 |
| DP03 | 129 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | All families | 82 | 0 | 82 |
| DP03 | 130 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | With related children of the householder under 18 years | 82 | 0 | 81 |
| DP03 | 131 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | With related children of the householder under 5 years only | 82 | 0 | 81 |
| DP03 | 132 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | Married couple families | 82 | 0 | 82 |
| DP03 | 133 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | With related children of the householder under 18 years | 82 | 0 | 81 |
| DP03 | 134 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | With related children of the householder under 5 years only | 82 | 0 | 81 |
| DP03 | 135 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | Families with female householder, no spouse present | 82 | 0 | 81 |
| DP03 | 136 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | With related children of the householder under 18 years | 82 | 0 | 81 |
| DP03 | 137 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | With related children of the householder under 5 years only | 82 | 0 | 81 |
| DP03 | 138 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | All people | 82 | 0 | 82 |
| DP03 | 139 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | Under 18 years | 82 | 0 | 81 |
| DP03 | 140 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | Related children of the householder under 18 years | 82 | 0 | 81 |
| DP03 | 141 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | Related children of the householder under 5 years | 82 | 0 | 81 |
| DP03 | 142 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | Related children of the householder 5 to 17 years | 82 | 0 | 81 |
| DP03 | 143 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | 18 years and over | 82 | 0 | 82 |
| DP03 | 144 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | 18 to 64 years | 82 | 0 | 82 |
| DP03 | 145 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | 65 years and over | 82 | 0 | 82 |
| DP03 | 146 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | People in families | 82 | 0 | 82 |
| DP03 | 147 | PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL | Unrelated individuals 15 years and over | 82 | 0 | 82 |
| DP04 | 4 | HOUSING OCCUPANCY | Total housing units | 82 | 82 | 82 |
| DP04 | 5 | HOUSING OCCUPANCY | Occupied housing units | 82 | 82 | 82 |
| DP04 | 6 | HOUSING OCCUPANCY | Vacant housing units | 82 | 82 | 82 |
| DP04 | 7 | HOUSING OCCUPANCY | Homeowner vacancy rate | 82 | 81 | 0 |
| DP04 | 8 | HOUSING OCCUPANCY | Rental vacancy rate | 82 | 82 | 0 |
| DP04 | 10 | UNITS IN STRUCTURE | Total housing units | 82 | 82 | 82 |
| DP04 | 11 | UNITS IN STRUCTURE | 1-unit, detached | 82 | 82 | 82 |
| DP04 | 12 | UNITS IN STRUCTURE | 1-unit, attached | 82 | 82 | 82 |
| DP04 | 13 | UNITS IN STRUCTURE | 2 units | 82 | 82 | 82 |
| DP04 | 14 | UNITS IN STRUCTURE | 3 or 4 units | 82 | 82 | 82 |
| DP04 | 15 | UNITS IN STRUCTURE | 5 to 9 units | 82 | 82 | 82 |
| DP04 | 16 | UNITS IN STRUCTURE | 10 to 19 units | 82 | 82 | 82 |
| DP04 | 17 | UNITS IN STRUCTURE | 20 or more units | 82 | 82 | 82 |
| DP04 | 18 | UNITS IN STRUCTURE | Mobile home | 82 | 82 | 82 |
| DP04 | 19 | UNITS IN STRUCTURE | Boat, RV, van, etc. | 82 | 82 | 82 |
| DP04 | 21 | YEAR STRUCTURE BUILT | Total housing units | 82 | 82 | 82 |
| DP04 | 22 | YEAR STRUCTURE BUILT | Built 2020 or later | 82 | 82 | 82 |
| DP04 | 23 | YEAR STRUCTURE BUILT | Built 2010 to 2019 | 82 | 82 | 82 |
| DP04 | 24 | YEAR STRUCTURE BUILT | Built 2000 to 2009 | 82 | 82 | 82 |
| DP04 | 25 | YEAR STRUCTURE BUILT | Built 1990 to 1999 | 82 | 82 | 82 |
| DP04 | 26 | YEAR STRUCTURE BUILT | Built 1980 to 1989 | 82 | 82 | 82 |
| DP04 | 27 | YEAR STRUCTURE BUILT | Built 1970 to 1979 | 82 | 82 | 82 |
| DP04 | 28 | YEAR STRUCTURE BUILT | Built 1960 to 1969 | 82 | 82 | 82 |
| DP04 | 29 | YEAR STRUCTURE BUILT | Built 1950 to 1959 | 82 | 82 | 82 |
| DP04 | 30 | YEAR STRUCTURE BUILT | Built 1940 to 1949 | 82 | 82 | 82 |
| DP04 | 31 | YEAR STRUCTURE BUILT | Built 1939 or earlier | 82 | 82 | 82 |
| DP04 | 33 | ROOMS | Total housing units | 82 | 82 | 82 |
| DP04 | 34 | ROOMS | 1 room | 82 | 82 | 82 |
| DP04 | 35 | ROOMS | 2 rooms | 82 | 82 | 82 |
| DP04 | 36 | ROOMS | 3 rooms | 82 | 82 | 82 |
| DP04 | 37 | ROOMS | 4 rooms | 82 | 82 | 82 |
| DP04 | 38 | ROOMS | 5 rooms | 82 | 82 | 82 |
| DP04 | 39 | ROOMS | 6 rooms | 82 | 82 | 82 |
| DP04 | 40 | ROOMS | 7 rooms | 82 | 82 | 82 |
| DP04 | 41 | ROOMS | 8 rooms | 82 | 82 | 82 |
| DP04 | 42 | ROOMS | 9 rooms or more | 82 | 82 | 82 |
| DP04 | 43 | ROOMS | Median rooms | 82 | 82 | 0 |
| DP04 | 45 | BEDROOMS | Total housing units | 82 | 82 | 82 |
| DP04 | 46 | BEDROOMS | No bedroom | 82 | 82 | 82 |
| DP04 | 47 | BEDROOMS | 1 bedroom | 82 | 82 | 82 |
| DP04 | 48 | BEDROOMS | 2 bedrooms | 82 | 82 | 82 |
| DP04 | 49 | BEDROOMS | 3 bedrooms | 82 | 82 | 82 |
| DP04 | 50 | BEDROOMS | 4 bedrooms | 82 | 82 | 82 |
| DP04 | 51 | BEDROOMS | 5 or more bedrooms | 82 | 82 | 82 |
| DP04 | 53 | HOUSING TENURE | Occupied housing units | 82 | 82 | 82 |
| DP04 | 54 | HOUSING TENURE | Owner-occupied | 82 | 82 | 82 |
| DP04 | 55 | HOUSING TENURE | Renter-occupied | 82 | 82 | 82 |
| DP04 | 56 | HOUSING TENURE | Average household size of owner-occupied unit | 82 | 81 | 0 |
| DP04 | 57 | HOUSING TENURE | Average household size of renter-occupied unit | 82 | 82 | 0 |
| DP04 | 59 | YEAR HOUSEHOLDER MOVED INTO UNIT | Occupied housing units | 82 | 82 | 82 |
| DP04 | 60 | YEAR HOUSEHOLDER MOVED INTO UNIT | Moved in 2023 or later | 82 | 82 | 82 |
| DP04 | 61 | YEAR HOUSEHOLDER MOVED INTO UNIT | Moved in 2020 to 2022 | 82 | 82 | 82 |
| DP04 | 62 | YEAR HOUSEHOLDER MOVED INTO UNIT | Moved in 2010 to 2019 | 82 | 82 | 82 |
| DP04 | 63 | YEAR HOUSEHOLDER MOVED INTO UNIT | Moved in 2000 to 2009 | 82 | 82 | 82 |
| DP04 | 64 | YEAR HOUSEHOLDER MOVED INTO UNIT | Moved in 1990 to 1999 | 82 | 82 | 82 |
| DP04 | 65 | YEAR HOUSEHOLDER MOVED INTO UNIT | Moved in 1989 and earlier | 82 | 82 | 82 |
| DP04 | 67 | VEHICLES AVAILABLE | Occupied housing units | 82 | 82 | 82 |
| DP04 | 68 | VEHICLES AVAILABLE | No vehicles available | 82 | 82 | 82 |
| DP04 | 69 | VEHICLES AVAILABLE | 1 vehicle available | 82 | 82 | 82 |
| DP04 | 70 | VEHICLES AVAILABLE | 2 vehicles available | 82 | 82 | 82 |
| DP04 | 71 | VEHICLES AVAILABLE | 3 or more vehicles available | 82 | 82 | 82 |
| DP04 | 73 | HOUSE HEATING FUEL | Occupied housing units | 82 | 82 | 82 |
| DP04 | 74 | HOUSE HEATING FUEL | Utility gas | 82 | 82 | 82 |
| DP04 | 75 | HOUSE HEATING FUEL | Bottled or tank gas (propane, butane, etc.) | 82 | 82 | 82 |
| DP04 | 76 | HOUSE HEATING FUEL | Electricity | 82 | 82 | 82 |
| DP04 | 77 | HOUSE HEATING FUEL | Fuel oil, kerosene, etc. | 82 | 82 | 82 |
| DP04 | 78 | HOUSE HEATING FUEL | Coal or coke | 82 | 82 | 82 |
| DP04 | 79 | HOUSE HEATING FUEL | Wood | 82 | 82 | 82 |
| DP04 | 80 | HOUSE HEATING FUEL | Solar energy | 82 | 82 | 82 |
| DP04 | 81 | HOUSE HEATING FUEL | Other fuel | 82 | 82 | 82 |
| DP04 | 82 | HOUSE HEATING FUEL | No fuel used | 82 | 82 | 82 |
| DP04 | 84 | SELECTED CHARACTERISTICS | Occupied housing units | 82 | 82 | 82 |
| DP04 | 85 | SELECTED CHARACTERISTICS | Lacking complete plumbing facilities | 82 | 82 | 82 |
| DP04 | 86 | SELECTED CHARACTERISTICS | Lacking complete kitchen facilities | 82 | 82 | 82 |
| DP04 | 87 | SELECTED CHARACTERISTICS | No telephone service available | 82 | 82 | 82 |
| DP04 | 89 | OCCUPANTS PER ROOM | Occupied housing units | 82 | 82 | 82 |
| DP04 | 90 | OCCUPANTS PER ROOM | 1.00 or less | 82 | 82 | 82 |
| DP04 | 91 | OCCUPANTS PER ROOM | 1.01 to 1.50 | 82 | 82 | 82 |
| DP04 | 92 | OCCUPANTS PER ROOM | 1.51 or more | 82 | 82 | 82 |
| DP04 | 94 | VALUE | Owner-occupied units | 82 | 82 | 82 |
| DP04 | 95 | VALUE | Less than $50,000 | 82 | 82 | 81 |
| DP04 | 96 | VALUE | $50,000 to $99,999 | 82 | 82 | 81 |
| DP04 | 97 | VALUE | $100,000 to $149,999 | 82 | 82 | 81 |
| DP04 | 98 | VALUE | $150,000 to $199,999 | 82 | 82 | 81 |
| DP04 | 99 | VALUE | $200,000 to $299,999 | 82 | 82 | 81 |
| DP04 | 100 | VALUE | $300,000 to $499,999 | 82 | 82 | 81 |
| DP04 | 101 | VALUE | $500,000 to $999,999 | 82 | 82 | 81 |
| DP04 | 102 | VALUE | $1,000,000 or more | 82 | 82 | 81 |
| DP04 | 103 | VALUE | Median (dollars) | 82 | 81 | 0 |
| DP04 | 105 | MORTGAGE STATUS | Owner-occupied units | 82 | 82 | 82 |
| DP04 | 106 | MORTGAGE STATUS | Housing units with a mortgage | 82 | 82 | 81 |
| DP04 | 107 | MORTGAGE STATUS | Housing units without a mortgage | 82 | 82 | 81 |
| DP04 | 109 | SELECTED MONTHLY OWNER COSTS (SMOC) | Housing units with a mortgage | 82 | 82 | 82 |
| DP04 | 110 | SELECTED MONTHLY OWNER COSTS (SMOC) | Less than $500 | 82 | 82 | 81 |
| DP04 | 111 | SELECTED MONTHLY OWNER COSTS (SMOC) | $500 to $999 | 82 | 82 | 81 |
| DP04 | 112 | SELECTED MONTHLY OWNER COSTS (SMOC) | $1,000 to $1,499 | 82 | 82 | 81 |
| DP04 | 113 | SELECTED MONTHLY OWNER COSTS (SMOC) | $1,500 to $1,999 | 82 | 82 | 81 |
| DP04 | 114 | SELECTED MONTHLY OWNER COSTS (SMOC) | $2,000 to $2,499 | 82 | 82 | 81 |
| DP04 | 115 | SELECTED MONTHLY OWNER COSTS (SMOC) | $2,500 to $2,999 | 82 | 82 | 81 |
| DP04 | 116 | SELECTED MONTHLY OWNER COSTS (SMOC) | $3,000 or more | 82 | 82 | 81 |
| DP04 | 117 | SELECTED MONTHLY OWNER COSTS (SMOC) | Median (dollars) | 82 | 80 | 0 |
| DP04 | 118 | SELECTED MONTHLY OWNER COSTS (SMOC) | Housing units without a mortgage | 82 | 82 | 82 |
| DP04 | 119 | SELECTED MONTHLY OWNER COSTS (SMOC) | Less than $250 | 82 | 82 | 81 |
| DP04 | 120 | SELECTED MONTHLY OWNER COSTS (SMOC) | $250 to $399 | 82 | 82 | 81 |
| DP04 | 121 | SELECTED MONTHLY OWNER COSTS (SMOC) | $400 to $599 | 82 | 82 | 81 |
| DP04 | 122 | SELECTED MONTHLY OWNER COSTS (SMOC) | $600 to $799 | 82 | 82 | 81 |
| DP04 | 123 | SELECTED MONTHLY OWNER COSTS (SMOC) | $800 to $999 | 82 | 82 | 81 |
| DP04 | 124 | SELECTED MONTHLY OWNER COSTS (SMOC) | $1,000 or more | 82 | 82 | 81 |
| DP04 | 125 | SELECTED MONTHLY OWNER COSTS (SMOC) | Median (dollars) | 82 | 81 | 0 |
| DP04 | 127 | SELECTED MONTHLY OWNER COSTS AS A PERCENTAGE OF HOUSEHOLD INCOME (SMOCAPI) | Housing units with a mortgage (excluding units where SMOCAPI cannot be computed) | 82 | 82 | 82 |
| DP04 | 128 | SELECTED MONTHLY OWNER COSTS AS A PERCENTAGE OF HOUSEHOLD INCOME (SMOCAPI) | Less than 20.0 percent | 82 | 82 | 81 |
| DP04 | 129 | SELECTED MONTHLY OWNER COSTS AS A PERCENTAGE OF HOUSEHOLD INCOME (SMOCAPI) | 20.0 to 24.9 percent | 82 | 82 | 81 |
| DP04 | 130 | SELECTED MONTHLY OWNER COSTS AS A PERCENTAGE OF HOUSEHOLD INCOME (SMOCAPI) | 25.0 to 29.9 percent | 82 | 82 | 81 |
| DP04 | 131 | SELECTED MONTHLY OWNER COSTS AS A PERCENTAGE OF HOUSEHOLD INCOME (SMOCAPI) | 30.0 to 34.9 percent | 82 | 82 | 81 |
| DP04 | 132 | SELECTED MONTHLY OWNER COSTS AS A PERCENTAGE OF HOUSEHOLD INCOME (SMOCAPI) | 35.0 percent or more | 82 | 82 | 81 |
| DP04 | 133 | SELECTED MONTHLY OWNER COSTS AS A PERCENTAGE OF HOUSEHOLD INCOME (SMOCAPI) | Not computed | 82 | 82 | 0 |
| DP04 | 134 | SELECTED MONTHLY OWNER COSTS AS A PERCENTAGE OF HOUSEHOLD INCOME (SMOCAPI) | Housing unit without a mortgage (excluding units where SMOCAPI cannot be computed) | 82 | 82 | 82 |
| DP04 | 135 | SELECTED MONTHLY OWNER COSTS AS A PERCENTAGE OF HOUSEHOLD INCOME (SMOCAPI) | Less than 10.0 percent | 82 | 82 | 81 |
| DP04 | 136 | SELECTED MONTHLY OWNER COSTS AS A PERCENTAGE OF HOUSEHOLD INCOME (SMOCAPI) | 10.0 to 14.9 percent | 82 | 82 | 81 |
| DP04 | 137 | SELECTED MONTHLY OWNER COSTS AS A PERCENTAGE OF HOUSEHOLD INCOME (SMOCAPI) | 15.0 to 19.9 percent | 82 | 82 | 81 |
| DP04 | 138 | SELECTED MONTHLY OWNER COSTS AS A PERCENTAGE OF HOUSEHOLD INCOME (SMOCAPI) | 20.0 to 24.9 percent | 82 | 82 | 81 |
| DP04 | 139 | SELECTED MONTHLY OWNER COSTS AS A PERCENTAGE OF HOUSEHOLD INCOME (SMOCAPI) | 25.0 to 29.9 percent | 82 | 82 | 81 |
| DP04 | 140 | SELECTED MONTHLY OWNER COSTS AS A PERCENTAGE OF HOUSEHOLD INCOME (SMOCAPI) | 30.0 to 34.9 percent | 82 | 82 | 81 |
| DP04 | 141 | SELECTED MONTHLY OWNER COSTS AS A PERCENTAGE OF HOUSEHOLD INCOME (SMOCAPI) | 35.0 percent or more | 82 | 82 | 81 |
| DP04 | 142 | SELECTED MONTHLY OWNER COSTS AS A PERCENTAGE OF HOUSEHOLD INCOME (SMOCAPI) | Not computed | 82 | 82 | 0 |
| DP04 | 144 | GROSS RENT | Occupied units paying rent | 82 | 82 | 82 |
| DP04 | 145 | GROSS RENT | Less than $500 | 82 | 82 | 82 |
| DP04 | 146 | GROSS RENT | $500 to $999 | 82 | 82 | 82 |
| DP04 | 147 | GROSS RENT | $1,000 to $1,499 | 82 | 82 | 82 |
| DP04 | 148 | GROSS RENT | $1,500 to $1,999 | 82 | 82 | 82 |
| DP04 | 149 | GROSS RENT | $2,000 to $2,499 | 82 | 82 | 82 |
| DP04 | 150 | GROSS RENT | $2,500 to $2,999 | 82 | 82 | 82 |
| DP04 | 151 | GROSS RENT | $3,000 or more | 82 | 82 | 82 |
| DP04 | 152 | GROSS RENT | Median (dollars) | 82 | 82 | 0 |
| DP04 | 153 | GROSS RENT | No rent paid | 82 | 82 | 0 |
| DP04 | 155 | GROSS RENT AS A PERCENTAGE OF HOUSEHOLD INCOME (GRAPI) | Occupied units paying rent (excluding units where GRAPI cannot be computed) | 82 | 82 | 82 |
| DP04 | 156 | GROSS RENT AS A PERCENTAGE OF HOUSEHOLD INCOME (GRAPI) | Less than 15.0 percent | 82 | 82 | 82 |
| DP04 | 157 | GROSS RENT AS A PERCENTAGE OF HOUSEHOLD INCOME (GRAPI) | 15.0 to 19.9 percent | 82 | 82 | 82 |
| DP04 | 158 | GROSS RENT AS A PERCENTAGE OF HOUSEHOLD INCOME (GRAPI) | 20.0 to 24.9 percent | 82 | 82 | 82 |
| DP04 | 159 | GROSS RENT AS A PERCENTAGE OF HOUSEHOLD INCOME (GRAPI) | 25.0 to 29.9 percent | 82 | 82 | 82 |
| DP04 | 160 | GROSS RENT AS A PERCENTAGE OF HOUSEHOLD INCOME (GRAPI) | 30.0 to 34.9 percent | 82 | 82 | 82 |
| DP04 | 161 | GROSS RENT AS A PERCENTAGE OF HOUSEHOLD INCOME (GRAPI) | 35.0 percent or more | 82 | 82 | 82 |
| DP04 | 162 | GROSS RENT AS A PERCENTAGE OF HOUSEHOLD INCOME (GRAPI) | Not computed | 82 | 82 | 0 |
| DP05 | 4 | SEX AND AGE | Total population | 82 | 82 | 82 |
| DP05 | 5 | SEX AND AGE | Male | 82 | 82 | 82 |
| DP05 | 6 | SEX AND AGE | Female | 82 | 82 | 82 |
| DP05 | 7 | SEX AND AGE | Sex ratio (males per 100 females) | 82 | 82 | 0 |
| DP05 | 8 | SEX AND AGE | Under 5 years | 82 | 82 | 82 |
| DP05 | 9 | SEX AND AGE | 5 to 9 years | 82 | 82 | 82 |
| DP05 | 10 | SEX AND AGE | 10 to 14 years | 82 | 82 | 82 |
| DP05 | 11 | SEX AND AGE | 15 to 19 years | 82 | 82 | 82 |
| DP05 | 12 | SEX AND AGE | 20 to 24 years | 82 | 82 | 82 |
| DP05 | 13 | SEX AND AGE | 25 to 34 years | 82 | 82 | 82 |
| DP05 | 14 | SEX AND AGE | 35 to 44 years | 82 | 82 | 82 |
| DP05 | 15 | SEX AND AGE | 45 to 54 years | 82 | 82 | 82 |
| DP05 | 16 | SEX AND AGE | 55 to 59 years | 82 | 82 | 82 |
| DP05 | 17 | SEX AND AGE | 60 to 64 years | 82 | 82 | 82 |
| DP05 | 18 | SEX AND AGE | 65 to 74 years | 82 | 82 | 82 |
| DP05 | 19 | SEX AND AGE | 75 to 84 years | 82 | 82 | 82 |
| DP05 | 20 | SEX AND AGE | 85 years and over | 82 | 82 | 82 |
| DP05 | 21 | SEX AND AGE | Median age (years) | 82 | 82 | 0 |
| DP05 | 22 | SEX AND AGE | Under 18 years | 82 | 82 | 82 |
| DP05 | 23 | SEX AND AGE | 16 years and over | 82 | 82 | 82 |
| DP05 | 24 | SEX AND AGE | 18 years and over | 82 | 82 | 82 |
| DP05 | 25 | SEX AND AGE | 21 years and over | 82 | 82 | 82 |
| DP05 | 26 | SEX AND AGE | 62 years and over | 82 | 82 | 82 |
| DP05 | 27 | SEX AND AGE | 65 years and over | 82 | 82 | 82 |
| DP05 | 28 | SEX AND AGE | 18 years and over | 82 | 82 | 82 |
| DP05 | 29 | SEX AND AGE | Male | 82 | 82 | 82 |
| DP05 | 30 | SEX AND AGE | Female | 82 | 82 | 82 |
| DP05 | 31 | SEX AND AGE | Sex ratio (males per 100 females) | 82 | 82 | 0 |
| DP05 | 32 | SEX AND AGE | 65 years and over | 82 | 82 | 82 |
| DP05 | 33 | SEX AND AGE | Male | 82 | 82 | 82 |
| DP05 | 34 | SEX AND AGE | Female | 82 | 82 | 82 |
| DP05 | 35 | SEX AND AGE | Sex ratio (males per 100 females) | 82 | 82 | 0 |
| DP05 | 37 | RACE | Total population | 82 | 82 | 82 |
| DP05 | 38 | RACE | One race | 82 | 82 | 82 |
| DP05 | 39 | RACE | Two or More Races | 82 | 82 | 82 |
| DP05 | 40 | RACE | One race | 82 | 82 | 82 |
| DP05 | 41 | RACE | White | 82 | 82 | 82 |
| DP05 | 42 | RACE | Egyptian | 82 | 82 | 82 |
| DP05 | 43 | RACE | English | 82 | 82 | 82 |
| DP05 | 44 | RACE | German | 82 | 82 | 82 |
| DP05 | 45 | RACE | Irish | 82 | 82 | 82 |
| DP05 | 46 | RACE | Italian | 82 | 82 | 82 |
| DP05 | 47 | RACE | Lebanese | 82 | 82 | 82 |
| DP05 | 48 | RACE | Other White | 82 | 82 | 82 |
| DP05 | 49 | RACE | Black or African American | 82 | 82 | 82 |
| DP05 | 50 | RACE | African American | 82 | 82 | 82 |
| DP05 | 51 | RACE | Ethiopian | 82 | 82 | 82 |
| DP05 | 52 | RACE | Haitian | 82 | 82 | 82 |
| DP05 | 53 | RACE | Jamaican | 82 | 82 | 82 |
| DP05 | 54 | RACE | Nigerian | 82 | 82 | 82 |
| DP05 | 55 | RACE | Somali | 82 | 82 | 82 |
| DP05 | 56 | RACE | Other Black or African American | 82 | 82 | 82 |
| DP05 | 57 | RACE | American Indian and Alaska Native | 82 | 82 | 82 |
| DP05 | 58 | RACE | Aztec | 82 | 82 | 82 |
| DP05 | 59 | RACE | Blackfeet Tribe of the Blackfeet Indian Reservation of Montana | 82 | 82 | 82 |
| DP05 | 60 | RACE | Maya | 82 | 82 | 82 |
| DP05 | 61 | RACE | Native Village of Barrow Inupiat Traditional Government | 82 | 82 | 82 |
| DP05 | 62 | RACE | Navajo Nation | 82 | 82 | 82 |
| DP05 | 63 | RACE | Nome Eskimo Community | 82 | 82 | 82 |
| DP05 | 64 | RACE | Other American Indian and Alaska Native | 82 | 82 | 82 |
| DP05 | 65 | RACE | Asian | 82 | 82 | 82 |
| DP05 | 66 | RACE | Asian Indian | 82 | 82 | 82 |
| DP05 | 67 | RACE | Chinese | 82 | 82 | 82 |
| DP05 | 68 | RACE | Filipino | 82 | 82 | 82 |
| DP05 | 69 | RACE | Japanese | 82 | 82 | 82 |
| DP05 | 70 | RACE | Korean | 82 | 82 | 82 |
| DP05 | 71 | RACE | Vietnamese | 82 | 82 | 82 |
| DP05 | 72 | RACE | Other Asian | 82 | 82 | 82 |
| DP05 | 73 | RACE | Native Hawaiian and Other Pacific Islander | 82 | 82 | 82 |
| DP05 | 74 | RACE | Chamorro | 82 | 82 | 82 |
| DP05 | 75 | RACE | Native Hawaiian | 82 | 82 | 82 |
| DP05 | 76 | RACE | Samoan | 82 | 82 | 82 |
| DP05 | 77 | RACE | Other Native Hawaiian and Other Pacific Islander | 82 | 82 | 82 |
| DP05 | 78 | RACE | Some Other Race | 82 | 82 | 82 |
| DP05 | 79 | RACE | Two or More Races | 82 | 82 | 82 |
| DP05 | 80 | RACE | White and Black or African American | 82 | 82 | 82 |
| DP05 | 81 | RACE | White and American Indian and Alaska Native | 82 | 82 | 82 |
| DP05 | 82 | RACE | White and Asian | 82 | 82 | 82 |
| DP05 | 83 | RACE | White and Some Other Race | 82 | 82 | 82 |
| DP05 | 84 | RACE | Black or African American and American Indian and Alaska Native | 82 | 82 | 82 |
| DP05 | 85 | RACE | Black or African American and Some Other Race | 82 | 82 | 82 |
| DP05 | 87 | Race alone or in combination with one or more other races | Total population | 82 | 82 | 82 |
| DP05 | 88 | Race alone or in combination with one or more other races | White | 82 | 82 | 82 |
| DP05 | 89 | Race alone or in combination with one or more other races | Black or African American | 82 | 82 | 82 |
| DP05 | 90 | Race alone or in combination with one or more other races | American Indian and Alaska Native | 82 | 82 | 82 |
| DP05 | 91 | Race alone or in combination with one or more other races | Asian | 82 | 82 | 82 |
| DP05 | 92 | Race alone or in combination with one or more other races | Native Hawaiian and Other Pacific Islander | 82 | 82 | 82 |
| DP05 | 93 | Race alone or in combination with one or more other races | Some Other Race | 82 | 82 | 82 |
| DP05 | 95 | HISPANIC OR LATINO AND RACE | Total population | 82 | 82 | 82 |
| DP05 | 96 | HISPANIC OR LATINO AND RACE | Hispanic or Latino (of any race) | 82 | 82 | 82 |
| DP05 | 97 | HISPANIC OR LATINO AND RACE | Mexican | 82 | 82 | 82 |
| DP05 | 98 | HISPANIC OR LATINO AND RACE | Puerto Rican | 82 | 82 | 82 |
| DP05 | 99 | HISPANIC OR LATINO AND RACE | Cuban | 82 | 82 | 82 |
| DP05 | 100 | HISPANIC OR LATINO AND RACE | Other Hispanic or Latino | 82 | 82 | 82 |
| DP05 | 101 | HISPANIC OR LATINO AND RACE | Not Hispanic or Latino | 82 | 82 | 82 |
| DP05 | 102 | HISPANIC OR LATINO AND RACE | White alone | 82 | 82 | 82 |
| DP05 | 103 | HISPANIC OR LATINO AND RACE | Black or African American alone | 82 | 82 | 82 |
| DP05 | 104 | HISPANIC OR LATINO AND RACE | American Indian and Alaska Native alone | 82 | 82 | 82 |
| DP05 | 105 | HISPANIC OR LATINO AND RACE | Asian alone | 82 | 82 | 82 |
| DP05 | 106 | HISPANIC OR LATINO AND RACE | Native Hawaiian and Other Pacific Islander alone | 82 | 82 | 82 |
| DP05 | 107 | HISPANIC OR LATINO AND RACE | Some Other Race alone | 82 | 82 | 82 |
| DP05 | 108 | HISPANIC OR LATINO AND RACE | Two or More Races | 82 | 82 | 82 |
| DP05 | 109 | HISPANIC OR LATINO AND RACE | Two races including Some Other Race | 82 | 82 | 82 |
| DP05 | 110 | HISPANIC OR LATINO AND RACE | Two races excluding Some Other Race, and three or more races | 82 | 82 | 82 |
| DP05 | 111 | HISPANIC OR LATINO AND RACE | Total housing units | 82 | 82 | 0 |
| DP05 | 113 | CITIZEN, VOTING AGE POPULATION | Citizen, 18 and over population | 82 | 82 | 82 |
| DP05 | 114 | CITIZEN, VOTING AGE POPULATION | Male | 82 | 82 | 82 |
| DP05 | 115 | CITIZEN, VOTING AGE POPULATION | Female | 82 | 82 | 82 |

## Audit evidence

The complete local audit is retained at `work/data-study/database-audit.json`. Metadata request outcomes are retained at `work/data-study/census-table-verification.json`; a timeout is not evidence that a table does not exist. Neither file contains OpenAI credentials.
