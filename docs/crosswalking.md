# Crosswalking and statistical uncertainty

`app/gis/crosswalk.py` supports only additive counts. Counts, source URLs and reference periods must be supplied. Each source geography's nonnegative finite weights must sum to one; duplicate pairs and incomplete coverage fail. Allocated totals must conserve the original counts.

Area-weighted allocation uses a Hawaiʻi Albers equal-area projection. Long geographic edges are densified to at most 0.0025 degrees before projection, so splitting an edge does not introduce substantial chord discrepancies. The user of the function must supply an explicit justification. Area weighting a demographic count implies a distributional assumption and is not a default ingestion policy.

Block-population weighting requires verified block population, source URLs and pre-established district assignments. Duplicate blocks, split blocks and zero-population denominators are refused. This module does not claim to have obtained a production tract-to-district population relationship; no such demographic crosswalk was run here.

Medians, rates, ratios and percentages cannot pass the count allocator. Rates may be recomputed from compatible numerator/denominator counts. Direct district ACS estimates take precedence over unnecessary crosswalking.

## Actual spatial benchmark

`make validate-crosswalk` uses the captured official 51 House and 25 Senate polygons. The additive quantity is polygon surface area itself: density is exactly one unit of area per unit of area, making area weighting defensible. It creates 99 actual nonzero House-to-Senate intersections, conserves the total area, and compares each allocated Senate polygon area against its directly measured area.

The observed maximum relative benchmark error was approximately `1.99e-12`. This validates geometric intersection and conservation; it does **not** validate population apportionment, infer residents, or imply a demographic uncertainty bound. Captured polygons include the service's represented surfaces; the result is not labelled land area.

## ACS uncertainty

Original ACS estimates and 90% MOEs are preserved. Negative/sentinel values become null with raw values retained. Sum MOEs use root-sum-of-squares, with covariance unavailable. Subset percentages use the Census approximation; if subtraction yields a negative radicand, the conservative general-ratio expression is used. No significance claim is made for district/county/state differences or overlapping survey estimates.

Allocation adds modelling uncertainty not captured by survey MOEs. All allocations return `estimated=true` and a limitation disclosure. No unsupported precision is claimed.
