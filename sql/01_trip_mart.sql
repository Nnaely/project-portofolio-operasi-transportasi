-- {{RAW}} is replaced by the pipeline with an escaped absolute directory.
-- There is no stable public trip ID. Retain reported records; do not invent deduplication.
CREATE OR REPLACE TABLE zones AS
SELECT * FROM read_csv_auto('{{RAW}}/taxi_zone_lookup.csv');

CREATE OR REPLACE TABLE trips AS
WITH source AS (
    SELECT filename AS source_file,
           regexp_extract(filename, 'yellow_tripdata_([0-9]{4}-[0-9]{2})', 1) AS source_month,
           tpep_pickup_datetime AS pickup_at, tpep_dropoff_datetime AS dropoff_at,
           PULocationID AS pickup_zone_id, DOLocationID AS dropoff_zone_id,
           payment_type, RatecodeID AS rate_code, trip_distance,
           fare_amount,
           date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime)/60.0 AS duration_minutes
    FROM read_parquet('{{RAW}}/yellow_tripdata_2025-*.parquet', union_by_name=true, filename=true)
), joined AS (
    SELECT s.*, p.Borough AS pickup_borough, d.Borough AS dropoff_borough,
           CASE WHEN pickup_zone_id=132 AND d.Borough='Manhattan' THEN 'JFK → Manhattan'
                WHEN pickup_zone_id=138 AND d.Borough='Manhattan' THEN 'LaGuardia → Manhattan'
                WHEN p.Borough='Manhattan' AND d.Borough='Manhattan' THEN 'Manhattan → Manhattan'
                ELSE 'Other routes' END AS route,
           CASE WHEN pickup_at < TIMESTAMP '2025-04-01' THEN 'train' ELSE 'holdout' END AS period,
           CAST(pickup_at AS DATE) AS pickup_date,
           strftime(pickup_at,'%Y-%m') AS month,
           hour(pickup_at) AS hour
    FROM source s
    LEFT JOIN zones p ON p.LocationID=s.pickup_zone_id
    LEFT JOIN zones d ON d.LocationID=s.dropoff_zone_id
)
SELECT *,
       CASE
         WHEN pickup_at IS NULL OR dropoff_at IS NULL THEN '01_missing_timestamp'
         WHEN pickup_at < TIMESTAMP '2025-01-01' OR pickup_at >= TIMESTAMP '2025-05-01'
              OR strftime(pickup_at,'%Y-%m') <> source_month THEN '02_outside_source_month'
         WHEN payment_type IS NULL OR payment_type NOT IN (1,2) THEN '03_outside_card_cash'
         WHEN rate_code IS NULL OR rate_code NOT IN (1,2) THEN '04_outside_ratecodes_1_2'
         WHEN CAST(pickup_at AS DATE)=DATE '2025-03-09' OR CAST(dropoff_at AS DATE)=DATE '2025-03-09' THEN '05_dst_transition_day'
         WHEN duration_minutes IS NULL OR duration_minutes <= 0 THEN '06_nonpositive_duration'
         WHEN trip_distance IS NULL OR trip_distance <= 0 THEN '07_nonpositive_distance'
         WHEN trip_distance > 100 THEN '08_distance_over_100mi'
         WHEN fare_amount IS NULL OR fare_amount <= 0 THEN '09_nonpositive_fare'
         WHEN fare_amount > 500 THEN '10_fare_over_500usd'
         WHEN duration_minutes < 1 THEN '11_duration_under_1min'
         WHEN duration_minutes > 180 THEN '12_duration_over_180min'
         WHEN pickup_borough IS NULL OR dropoff_borough IS NULL
              OR pickup_borough IN ('Unknown','N/A') OR dropoff_borough IN ('Unknown','N/A') THEN '13_unknown_zone'
         ELSE 'eligible'
       END AS cohort_status,
       (pickup_at IS NOT NULL AND dropoff_at IS NOT NULL
        AND pickup_at >= TIMESTAMP '2025-01-01' AND pickup_at < TIMESTAMP '2025-05-01'
        AND strftime(pickup_at,'%Y-%m')=source_month
        AND payment_type IN (1,2) AND rate_code IN (1,2)
        AND CAST(pickup_at AS DATE)<>DATE '2025-03-09' AND CAST(dropoff_at AS DATE)<>DATE '2025-03-09'
        AND duration_minutes>0 AND duration_minutes<=240
        AND trip_distance>0 AND trip_distance<=100
        AND fare_amount>0 AND fare_amount<=1000
        AND pickup_borough NOT IN ('Unknown','N/A') AND dropoff_borough NOT IN ('Unknown','N/A')) AS broad_eligible
FROM joined;

CREATE OR REPLACE VIEW eligible_trips AS SELECT * FROM trips WHERE cohort_status='eligible';
CREATE OR REPLACE VIEW comparison_trips AS SELECT * FROM eligible_trips WHERE route <> 'Other routes';
