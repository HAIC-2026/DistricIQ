# Thirty-question implementation evaluation

Verified October 27, 2026, Pacific/Honolulu. These are live model and PostgreSQL results from the bounded answer service, including final rechecks after universe guards. All returned values/MOEs were reconciled; required-measure and limitation assertions passed. Partial answers do not establish the exact requested combined statistic.

| Question | Outcome | Retrieved indicators/programs | Result |
| --- | --- | --- | --- |
| 1. How many kūpuna in my district rely on Social Security as their primary income? | partially answerable | dp03_r074_estimate, older_adults_living_alone, dp03_r145_percent | Passed source reconciliation and configured intent checks |
| 2. What percentage of residents in my district are 65 or older? | directly answerable | older_adult_share | Passed source reconciliation and configured intent checks |
| 3. How many kūpuna in my district live below the poverty line? | supported calculation | older_poverty_count | Passed source reconciliation and configured intent checks |
| 4. Are older residents in my district more likely to rent or own their homes? | partially answerable | older_owner_households, older_renter_households | Passed source reconciliation and configured intent checks |
| 5. How does the kūpuna population in my district compare with the statewide average? | supported calculation | older_adult_share | Passed source reconciliation and configured intent checks |
| 6. How many older adults live alone in my district? | supported calculation | older_adults_living_alone | Passed source reconciliation and configured intent checks |
| 7. How many families in my district struggle to afford basic necessities? | partially answerable | dp03_r129_percent | Passed source reconciliation and configured intent checks |
| 8. What percentage of households spend more than 30% of their income on housing? | supported calculation | housing_burden_30_plus_share | Passed source reconciliation and configured intent checks |
| 9. How many households in my district earn less than $50,000 annually? | supported calculation | household_income_under_50000 | Passed source reconciliation and configured intent checks |
| 10. Are residents in my district experiencing higher poverty rates than neighboring districts? | supported calculation | poverty_rate | Passed source reconciliation and configured intent checks |
| 11. How does median household income compare with median rent in my district? | directly answerable | median_gross_rent, median_household_income | Passed source reconciliation and configured intent checks |
| 12. How many households rely on government assistance as a source of income? | partially answerable | dp03_r080_estimate, dp03_r074_estimate, dp03_r076_estimate | Passed source reconciliation and configured intent checks |
| 13. How many renters in my district are considered severely cost-burdened? | directly answerable | B25070_010 | Passed source reconciliation and configured intent checks |
| 14. What percentage of residents in my district live in owner-occupied housing? | partially answerable | owner_household_share | Passed source reconciliation and configured intent checks |
| 15. Are housing costs higher in my district than in the rest of Honolulu County? | partially answerable | median_gross_rent | Passed source reconciliation and configured intent checks |
| 16. How many households might be at risk of housing instability? | partially answerable | housing_burden_30_plus | Passed source reconciliation and configured intent checks |
| 17. What are the biggest housing-related challenges shown by my district’s demographic data? | directly answerable | median_gross_rent, rent_burden_35_plus, B25070_010 | Passed source reconciliation and configured intent checks |
| 18. Are there more renters or homeowners in my district? | directly answerable | owner_occupied, renter_occupied | Passed source reconciliation and configured intent checks |
| 19. How many children under 18 live in my district? | directly answerable | age_under_18 | Passed source reconciliation and configured intent checks |
| 20. What percentage of households have children under 18? | directly answerable | dp02_r017_percent | Passed source reconciliation and configured intent checks |
| 21. How many children live in households below the poverty line? | supported calculation | child_poverty_count | Passed source reconciliation and configured intent checks |
| 22. What percentage of adults have a bachelor’s degree or higher? | directly answerable | dp02_r078_percent | Passed source reconciliation and configured intent checks |
| 23. How many grandparents are responsible for raising their grandchildren? | directly answerable | dp02_r052_estimate | Passed source reconciliation and configured intent checks |
| 24. How does educational attainment in my district compare with the statewide average? | supported calculation | dp02_r070_percent, dp02_r071_percent, dp02_r072_percent, dp02_r073_percent, dp02_r074_percent | Passed source reconciliation and configured intent checks |
| 25. Which government assistance programs might be relevant to low-income kūpuna in my district? | program information | ; programs: snap, ssi, hcv, extra-help, medquest | Passed source reconciliation and configured intent checks |
| 26. How many residents might benefit from affordable housing assistance? | partially answerable | housing_burden_30_plus | Passed source reconciliation and configured intent checks |
| 27. What demographic indicators suggest a need for food assistance programs? | partially answerable | B17001_002, dp03_r082_estimate, dp03_r080_estimate | Passed source reconciliation and configured intent checks |
| 28. Which existing programs support older adults with limited retirement income? | program information | ; programs: extra-help, ssi, aging-services, kupuna-care, medquest | Passed source reconciliation and configured intent checks |
| 29. What information would be needed to estimate how many households might qualify for SNAP? | program information | ; programs: snap | Passed source reconciliation and configured intent checks |
| 30. What demographic trends could help government agencies plan community services? | partially answerable | median_household_income, poverty_rate, median_gross_rent, population, median_age, older_adult_share | Passed source reconciliation and configured intent checks |

Observed totals: 9 direct statistical answers; 8 calculations/comparisons; 3 program-information answers; 10 partial/contextual answers. No empty unsupported fallback occurred; exact unavailable measures remain unsupported within contextual answers.

See [full responses](research-30-question-live.json), [implementation report](research-expansion-report.md), and [HTTP source verification](research-http-verification.json). This evaluation is not universal proof of natural-language coverage.
