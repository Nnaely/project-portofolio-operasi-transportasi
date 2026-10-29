-- Q1: What does each occupied route-hour collect in base fare?
-- Never average individual trip fare/hour ratios; short trips can dominate that average.
SELECT period, route, COUNT(*) AS trips, SUM(fare_amount) AS fare_usd,
       SUM(duration_minutes) AS occupied_minutes,
       60*SUM(fare_amount)/SUM(duration_minutes) AS fare_per_occupied_hour
FROM comparison_trips GROUP BY period,route ORDER BY period,fare_per_occupied_hour DESC;

-- Q2: Does the Q1 ordering persist in April? No thresholds are retuned on April.
WITH grouped AS (
    SELECT period,route,COUNT(*) AS trips,
           60*SUM(fare_amount)/SUM(duration_minutes) AS fare_per_occupied_hour
    FROM comparison_trips GROUP BY period,route HAVING COUNT(*)>=1000
)
SELECT *,DENSE_RANK() OVER(PARTITION BY period ORDER BY fare_per_occupied_hour DESC) AS rank
FROM grouped ORDER BY period,rank;

-- Q3: Is pickup time an important operational dimension?
SELECT period,route,hour,COUNT(*) AS trips,
       60*SUM(fare_amount)/SUM(duration_minutes) AS fare_per_occupied_hour
FROM comparison_trips GROUP BY period,route,hour ORDER BY period,route,hour;

-- Q4: Daily totals preserve the common day shocks for a paired-day bootstrap.
SELECT period,pickup_date,route,COUNT(*) AS trips,
       SUM(fare_amount) AS fare_usd,SUM(duration_minutes) AS occupied_minutes
FROM comparison_trips GROUP BY period,pickup_date,route ORDER BY period,pickup_date,route;

-- Q5: Transparent mutually exclusive quality waterfall.
SELECT cohort_status,COUNT(*) AS records FROM trips GROUP BY cohort_status ORDER BY cohort_status;
