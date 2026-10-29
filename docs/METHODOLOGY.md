# Methodology

*Documentation by Nakata - Making this study easier to understand.*

## The decision and its boundary

The project asks whether airport-to-Manhattan trips justify further investigation as a staging strategy, compared with trips that start and end in Manhattan. It compares recorded base fare with time carrying a passenger, then shows how assumed empty time changes that comparison.

A high fare per occupied hour does not establish high driver income. The public records do not identify complete driver shifts, airport queues, repositioning time, all tips, or operating costs. This is a historical comparison and a measurement plan; it is not a dispatch recommendation ready for use.

## Source and reproducibility

The inputs are the official NYC Taxi and Limousine Commission Yellow Taxi monthly files for January–April 2025 and the official Taxi Zone Lookup Table. The [TLC source page](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) links both. TLC receives the records from technology providers and does not guarantee their accuracy. The downloaded file, month, retrieval details, and hashes are recorded in the project source manifest so the analysis can be tied to a specific download.

Field interpretation follows the [Yellow Taxi data dictionary, dated March 18, 2025](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf). Payment code 0 means Flex Fare; it is not a missing-payment code. Cash tips are absent. The separate CBD congestion fee applies from January 5, 2025. These facts matter when choosing the population and interpreting fare fields.

Source data are attributed to NYC TLC. The [NYC Open Data terms](https://data.cityofnewyork.us/stories/s/Terms-of-Use/k9k7-3cje/) and [NYC.gov terms](https://www.nyc.gov/main/terms-of-use) govern source access. The city's [technical manual, section 2.3.2](https://www.nyc.gov/assets/doitt/downloads/pdf/nyc_open_data_tsm.pdf) describes published open data as a public resource without licensing requirements. This project does not assign a Creative Commons license to NYC data or imply NYC endorsement.

## Population and comparisons

One source row represents one reported trip. A month filename is not enough to establish the trip date: eligibility requires the recorded pickup month to match the source filename and the analysis window. Reported records are retained rather than deduplicated without a stable public trip ID. The main comparison uses these mutually exclusive routes:

| Route | Pickup | Drop-off |
|---|---|---|
| JFK to Manhattan | Taxi zone 132 | A lookup-table zone whose borough is Manhattan |
| LaGuardia to Manhattan | Taxi zone 138 | A lookup-table zone whose borough is Manhattan |
| Manhattan to Manhattan | A lookup-table zone whose borough is Manhattan | A lookup-table zone whose borough is Manhattan |

These are geographic groups, not evidence of airport intent, a driver's previous trip, or the next passenger's destination. Lookup joins must retain trip-row counts; an unmapped or unknown location cannot be silently treated as Manhattan.

The primary scope is recorded credit-card or cash payment (`payment_type` 1 or 2), standard or JFK rate code (`RatecodeID` 1 or 2), pickup from January 1 through April 30, positive base fare no greater than USD 500, positive distance no greater than 100 miles, and duration from 1 to 180 minutes. These are declared plausibility limits, not proof that excluded trips are false. A broader sensitivity retains positive durations up to 240 minutes and fares up to USD 1,000, with the other rules unchanged.

Timestamps are used in their recorded NYC clock context, not converted to the viewer's time zone. Trips with pickup **or drop-off on March 9, 2025** are excluded because naïve clock subtraction around the spring daylight-saving transition can add an hour to an elapsed trip. This conservative choice also excludes valid trips on that day. The quality output assigns each excluded record its first failing rule, so the waterfall adds back to the input count; those counts are not independent failure totals. Both locations must map to a known borough. Missing passenger counts do not, by themselves, make fare and timing unusable.

Clean-data totals include other known routes. The three-route comparison is a subset of those totals; its trip count must not be presented as the count of all eligible Yellow Taxi trips. In the current build, 15,168,579 source records become 11,044,733 eligible records across known routes, of which 10,148,555 belong to the three comparison routes. The largest first-failure exclusion is 3,448,522 records outside card/cash scope; exclusion does not make all of these records erroneous.

## What the main metric means

For a route, **base fare per occupied hour = sum of `fare_amount` / sum of occupied minutes × 60**. The numerator excludes tips, tolls, taxes, airport charges, and congestion surcharges. The denominator includes only recorded pickup-to-drop-off time. A stopped vehicle with the meter engaged is still part of this occupied interval.

This ratio of totals gives every occupied minute the same weight. It is not the unweighted mean of each trip's fare-per-hour ratio, which can let a handful of very short trips dominate. Mean fare and mean duration are also shown so the ratio can be reconstructed.

## Time separation and uncertainty

January–March is the calibration period; April is the later comparison period. Route rankings are formed within the declared scope with a minimum of 1,000 trips. This minimum is a reporting rule, not a guarantee of statistical power. All six period/route groups exceed it. April is used to inspect whether the descriptive ordering persists. It is not a randomized test or evidence that sending additional drivers to airports causes a gain.

Uncertainty is estimated by resampling calendar days, using the same sampled days across routes. The calendar contains 89 eligible Q1 dates and 30 April dates, with absent route/day totals filled with zero rather than dropping quiet days. This preserves shared day-level conditions in each comparison more faithfully than independently resampling millions of trips. The analysis uses 2,000 bootstrap draws and the 2.5th and 97.5th percentiles. These intervals cannot repair source errors, route selection, unobserved driver differences, or dependence across adjacent days. Public data lack a driver ID for driver-cluster inference.

## Waiting-time scenario

The current April results are USD 83.39 per occupied hour for LaGuardia, USD 78.60 for JFK, and USD 64.31 for Manhattan-to-Manhattan. The Q1 ordering persists in April, but all three rates decrease. The broader duration/fare sensitivity preserves the ordering too. These checks establish descriptive stability within the chosen data; they do not validate missing empty-time assumptions.

For `n` trips and an assumed extra `w` minutes per trip:

`scenario fare per hour = 60 × total base fare / (total occupied minutes + n × w)`

The airport and city assumptions are separate. Extra minutes represent the combined unobserved time assigned to waiting and repositioning. They are not measured queue times. The scenario holds the observed trip mix, base fares, and occupied durations constant; real demand, driver competition, and congestion may change when behavior changes.

For an airport route, the break-even extra minutes against a specified city scenario are:

`60 × airport mean fare / city scenario fare per hour − airport mean occupied minutes`

A negative result means the airport route already trails that city scenario at zero extra minutes. A positive result is a hypothetical allowance, not a recommendation to join a queue of that length. The number does not include expenses or establish a profit threshold.

For example, using April observations and **10 assumed city extra minutes**, the break-even total extra time is 41.61 minutes per LaGuardia trip and 64.17 per JFK trip. With **30 assumed airport extra minutes**, scenario rates are USD 42.54 for LaGuardia and USD 50.38 for JFK, versus USD 35.76 for the city scenario. The airport ordering reverses relative to occupied time alone. This reversal is a consequence of the stated assumptions, not a measured result of airport operations.

Numeric values are rounded for reading; calculations use unrounded totals in `outputs/metrics.json`, `groups.csv`, `default_scenario.csv`, and `break_even_scenarios.csv`. The default 10/30-minute assumptions are illustrative and have no empirical waiting-time estimate behind them.

## Observed, assumed, and unmeasured

| Category | What belongs here |
|---|---|
| Observed in these records | Trip timestamps, locations, reported distance, fare fields, payment/rate codes, route summaries, and exclusions. |
| Chosen by the analyst | Date windows, quality thresholds, route definitions, minimum sample size, and bootstrap procedure. |
| Scenario assumptions | Extra minutes per trip and the premise that the recorded fare/duration mix stays unchanged. |
| Not established | Actual queue time, full-shift productivity, net driver income, profit, a causal treatment effect, or applicability to Indonesian transport operations. |

The experiment plan specifies what new measurements would be needed before testing an operational recommendation. No pilot has been run for this portfolio project.
