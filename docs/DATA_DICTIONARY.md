# Data dictionary and metric contract

*Documentation by Nakata - Making this study easier to understand.*

The source files are `yellow_tripdata_2025-01.parquet` through `yellow_tripdata_2025-04.parquet`, plus `taxi_zone_lookup.csv`. Download links originate from [NYC TLC](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page). Exact input hashes and row counts belong in the generated source manifest; eligibility counts belong in the quality report.

## Source fields used to define the analysis

| Field | Meaning in this project | Important handling |
|---|---|---|
| `tpep_pickup_datetime` | Start of the recorded occupied interval. | Defines month and date eligibility. |
| `tpep_dropoff_datetime` | End of that interval. | Must follow pickup within the declared duration bounds. |
| `PULocationID` | Pickup taxi-zone key. | Joined to `LocationID`; 132 = JFK, 138 = LaGuardia. |
| `DOLocationID` | Drop-off taxi-zone key. | Joined separately to the same lookup. |
| `LocationID` | Unique key of the zone lookup. | A duplicated lookup key would multiply trip rows and must fail validation. |
| `Borough` | Administrative area from the lookup. | Both geographic joins distinguish Manhattan from airport locations. |
| `Zone` | Human-readable zone label. | A label is not a driver or route identifier. |
| `trip_distance` | Reported miles while metered. | Quality filter; not total shift mileage. |
| `fare_amount` | Recorded base fare in USD. | Main numerator; kept separate from fees, tips, and tolls. |
| `payment_type` | Payment classification. | Main cohort: 1 credit card and 2 cash. Code 0 is Flex Fare and is outside this scope. |
| `RatecodeID` | Fare-rate classification. | Main cohort: 1 standard and 2 JFK; not all fares are distance-metered. |

The [official Yellow Taxi dictionary](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf) defines the remaining fields. In particular, `tip_amount` omits cash tips; `total_amount` is a passenger charge and also omits cash tips. `airport_fee`, `congestion_surcharge`, and `cbd_congestion_fee` are separate charge fields, not additions to the base-fare productivity numerator. The CBD field reflects the charge introduced January 5, 2025. These distinctions prevent passenger spending from being mislabeled as driver profit.

Vendor IDs identify reporting technology providers, not individual drivers. No driver-shift reconstruction is possible from these files. Trip records also lack a guaranteed unique trip key; identical field values alone do not prove that two reported trips are the same real-world event.

## Derived measures

| Measure | Unit | Definition |
|---|---|---|
| `duration_minutes` | Minutes | Recorded drop-off minus recorded pickup, subject to date/DST and plausibility rules. |
| `trips` | Reported trips | Number of eligible source rows in the group. |
| `fare_usd` | USD | Sum of eligible `fare_amount`. |
| `occupied_minutes` | Minutes | Sum of eligible occupied duration. |
| `mean_fare_usd` | USD/trip | `fare_usd / trips`. |
| `mean_minutes` | Minutes/trip | `occupied_minutes / trips`. |
| `fare_per_occupied_hour` | USD/occupied hour | `60 × fare_usd / occupied_minutes`. |
| Ratio to city | Multiple | Route productivity / Manhattan-to-Manhattan productivity for the same period and definition. |
| Scenario productivity | USD/(occupied + assumed empty hour) | `60 × fare_usd / (occupied_minutes + trips × assumed_extra_minutes)`. |
| Break-even extra time | Minutes/trip | Airport extra time at which airport and the specified city scenario have equal base-fare productivity. |

`period = train` means January–March 2025; `period = holdout` means April 2025. These labels describe a time split for a descriptive comparison. They do not imply a trained prediction model. USD is not converted to rupiah, and minutes are not business/paid shift minutes.

## Grain and denominator

Raw data have one row per reported trip. Route summaries have one row per period and route. Daily summaries have one row per date and route and support the paired day bootstrap. Combining summaries requires summing fare and duration before recalculating productivity; averaging route/month rates without weights changes the metric.

The SQL mart renames the timestamp fields to `pickup_at` and `dropoff_at`, location keys to `pickup_zone_id` and `dropoff_zone_id`, and `RatecodeID` to `rate_code`. It adds `source_file`, `source_month`, `pickup_date`, `month`, `hour`, `pickup_borough`, `dropoff_borough`, `route`, `period`, `cohort_status`, and `broad_eligible`. `cohort_status` records the first failing rule or `eligible`; `broad_eligible` is a separate sensitivity flag. `eligible_trips` includes other known routes, whereas `comparison_trips` contains only the three target route groups.

Card and cash records, the two selected rate codes, and the quality rules determine the denominator. Flex Fare, disputed/voided/no-charge records, other rate codes, unknown geographic routes, and implausible records must not silently re-enter chart totals. Quality exclusions narrow this study's scope; they do not imply those rides never occurred.

## Data use

Attribution: New York City Taxi and Limousine Commission, Yellow Taxi Trip Records, January–April 2025; official Taxi Zone Lookup Table. Sources are governed by [NYC Open Data terms](https://data.cityofnewyork.us/stories/s/Terms-of-Use/k9k7-3cje/) and [NYC.gov terms](https://www.nyc.gov/main/terms-of-use). No Creative Commons license or agency endorsement is asserted for this data. The project modifies source data through filtering, geographic joins, and aggregation; it is not an official TLC report.
