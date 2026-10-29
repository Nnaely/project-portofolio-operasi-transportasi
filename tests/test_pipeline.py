"""Small adversarial fixtures test actual SQL semantics, not the historical answers."""
import sys
from pathlib import Path
import tempfile
import unittest
import duckdb
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from analyze import weighted_rate, scenario_rate, break_even_minutes

def fixture(**overrides):
    row={"tpep_pickup_datetime":pd.Timestamp("2025-01-15 10:00:00"),
         "tpep_dropoff_datetime":pd.Timestamp("2025-01-15 10:20:00"),
         "PULocationID":132,"DOLocationID":100,"payment_type":1,"RatecodeID":2,
         "trip_distance":18.0,"fare_amount":70.0}
    row.update(overrides)
    return row

class MetricTests(unittest.TestCase):
    def test_ratio_of_totals_is_not_mean_trip_ratio(self):
        self.assertAlmostEqual(weighted_rate([20,20],[10,50]),40)
        self.assertNotAlmostEqual(weighted_rate([20,20],[10,50]),(120+24)/2)
    def test_extra_time_reduces_rate(self):
        self.assertGreater(scenario_rate(100,60,2,0),scenario_rate(100,60,2,10))
        with self.assertRaises(ValueError):scenario_rate(100,60,2,-1)
    def test_break_even_satisfies_original_formula(self):
        extra=break_even_minutes(70,40,60)
        self.assertAlmostEqual(extra,30)
        self.assertAlmostEqual(scenario_rate(70,40,1,extra),60)
    def test_negative_break_even_is_retained(self):
        self.assertLess(break_even_minutes(20,40,60),0)

class SQLTests(unittest.TestCase):
    def run_rows(self,rows,month="2025-01"):
        with tempfile.TemporaryDirectory() as d:
            raw=Path(d)
            pd.DataFrame({"LocationID":[100,132,138,264],"Borough":["Manhattan","Queens","Queens","Unknown"],
                          "Zone":["City","JFK","LGA","Unknown"],"service_zone":["Yellow Zone"]*4}).to_csv(raw/"taxi_zone_lookup.csv",index=False)
            con=duckdb.connect()
            con.register("fixture",pd.DataFrame(rows))
            path=(raw/f"yellow_tripdata_{month}.parquet").as_posix().replace("'","''")
            con.execute(f"COPY fixture TO '{path}' (FORMAT PARQUET)")
            sql=(ROOT/"sql"/"01_trip_mart.sql").read_text(encoding="utf-8").replace("{{RAW}}",raw.as_posix().replace("'","''"))
            con.execute(sql)
            result=con.execute("SELECT * FROM trips").df();con.close()
        return result
    def test_route_classification_and_unknown_zone(self):
        result=self.run_rows([fixture(),fixture(PULocationID=138,RatecodeID=1),fixture(PULocationID=100,RatecodeID=1),fixture(DOLocationID=264)])
        self.assertEqual(set(result[result.cohort_status=="eligible"].route),{"JFK → Manhattan","LaGuardia → Manhattan","Manhattan → Manhattan"})
        self.assertEqual(result[result.dropoff_zone_id==264].cohort_status.iloc[0],"13_unknown_zone")
    def test_no_fanout_and_no_unjustified_deduplication(self):
        result=self.run_rows([fixture(),fixture()])
        self.assertEqual(len(result),2)
        self.assertEqual(result.fare_amount.sum(),140)
    def test_zero_duration_and_primary_broad_boundary(self):
        result=self.run_rows([fixture(tpep_dropoff_datetime=pd.Timestamp("2025-01-15 10:00:00")),fixture(tpep_dropoff_datetime=pd.Timestamp("2025-01-15 10:00:30")),fixture(tpep_dropoff_datetime=pd.Timestamp("2025-01-15 13:00:00"))])
        self.assertEqual(set(result.cohort_status),{"06_nonpositive_duration","11_duration_under_1min","eligible"})
        self.assertTrue(result[result.duration_minutes==.5].broad_eligible.iloc[0])
        self.assertFalse(result[result.duration_minutes==0].broad_eligible.iloc[0])
    def test_payment_zero_flex_fare_and_rate_exclusions(self):
        result=self.run_rows([fixture(payment_type=0),fixture(RatecodeID=6)])
        self.assertEqual(set(result.cohort_status),{"03_outside_card_cash","04_outside_ratecodes_1_2"})
    def test_source_month_and_holdout(self):
        result=self.run_rows([fixture(tpep_pickup_datetime=pd.Timestamp("2025-04-01 10:00"),tpep_dropoff_datetime=pd.Timestamp("2025-04-01 10:20")),fixture()],month="2025-04")
        self.assertEqual(result[result.cohort_status=="eligible"].period.iloc[0],"holdout")
        self.assertEqual(result[result.month=="2025-01"].cohort_status.iloc[0],"02_outside_source_month")
    def test_dst_pickup_or_dropoff_is_excluded(self):
        result=self.run_rows([fixture(tpep_pickup_datetime=pd.Timestamp("2025-03-09 01:55"),tpep_dropoff_datetime=pd.Timestamp("2025-03-09 03:05")),fixture(tpep_pickup_datetime=pd.Timestamp("2025-03-08 23:55"),tpep_dropoff_datetime=pd.Timestamp("2025-03-09 00:10"))],month="2025-03")
        self.assertTrue((result.cohort_status=="05_dst_transition_day").all())
        self.assertFalse(result.broad_eligible.any())
    def test_fare_threshold_not_revenue(self):
        result=self.run_rows([fixture(fare_amount=500),fixture(fare_amount=501),fixture(fare_amount=0)])
        self.assertEqual(set(result.cohort_status),{"eligible","10_fare_over_500usd","09_nonpositive_fare"})
        self.assertTrue(result[result.fare_amount==501].broad_eligible.iloc[0])

if __name__=="__main__":unittest.main()
