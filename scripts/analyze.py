"""Reproducible NYC taxi route economics: base fare per occupied hour, not driver earnings.

Run download_data.py first. All source timestamps are treated as New York local
wall-clock timestamps. The spring DST transition day is excluded explicitly.
"""
from __future__ import annotations
from datetime import datetime, timezone
import json
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs"
CITY="Manhattan → Manhattan"
ROUTES=[CITY,"LaGuardia → Manhattan","JFK → Manhattan"]
SEED=20251014
REPLICATES=2000

def weighted_rate(fare,minutes):
    """Ratio of totals, never mean of per-trip ratios."""
    return 60*float(np.sum(fare))/float(np.sum(minutes)) if np.sum(minutes)>0 else None

def scenario_rate(fare,occupied_minutes,trips,extra_minutes):
    if extra_minutes<0:raise ValueError("Assumed extra time must be nonnegative")
    return 60*fare/(occupied_minutes+trips*extra_minutes)

def break_even_minutes(mean_fare,mean_minutes,city_rate):
    return mean_fare/city_rate*60-mean_minutes

def safe(v):
    if isinstance(v,dict):return {str(k):safe(val) for k,val in v.items()}
    if isinstance(v,(list,tuple)):return [safe(i) for i in v]
    if isinstance(v,np.generic):return safe(v.item())
    if isinstance(v,float) and not np.isfinite(v):return None
    if isinstance(v,(pd.Timestamp,datetime)):return v.isoformat()
    if v is pd.NA:return None
    return v

def save_json(name,data):
    (OUT/name).write_text(json.dumps(safe(data),indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def summarize(con,dimensions,where="cohort_status='eligible' AND route <> 'Other routes'"):
    fields=", ".join(dimensions)
    return con.execute(f"""SELECT {fields},count(*) AS trips,
        sum(fare_amount) AS fare_usd,sum(duration_minutes) AS occupied_minutes,
        sum(trip_distance) AS distance_miles,avg(fare_amount) AS mean_fare_usd,
        avg(duration_minutes) AS mean_minutes,
        60*sum(fare_amount)/sum(duration_minutes) AS fare_per_occupied_hour
        FROM trips WHERE {where} GROUP BY {fields} ORDER BY {fields}""").df()

def paired_day_bootstrap(daily,groups):
    rng=np.random.default_rng(SEED)
    cis={}; comparisons=[]; completeness=[]
    for period,start,end in [("train","2025-01-01","2025-03-31"),("holdout","2025-04-01","2025-04-30")]:
        days=pd.date_range(start,end).difference(pd.DatetimeIndex(["2025-03-09"]))
        ds=daily[daily.period==period].copy()
        ds["pickup_date"]=pd.to_datetime(ds.pickup_date)
        fares=ds.pivot(index="pickup_date",columns="route",values="fare_usd").reindex(index=days,columns=ROUTES).fillna(0).to_numpy()
        minutes=ds.pivot(index="pickup_date",columns="route",values="occupied_minutes").reindex(index=days,columns=ROUTES).fillna(0).to_numpy()
        draw=rng.integers(0,len(days),size=(REPLICATES,len(days)))
        rates=60*fares[draw].sum(axis=1)/minutes[draw].sum(axis=1)
        for col,route in enumerate(ROUTES):
            ci=np.quantile(rates[:,col],[.025,.975])
            cis[(period,route)]=(float(ci[0]),float(ci[1]))
            if route!=CITY:
                ratio=rates[:,col]/rates[:,0]
                p=groups[(groups.period==period)].set_index("route")
                comparisons.append({"period":period,"route":route,
                    "ratio_to_city":float(p.loc[route,"fare_per_occupied_hour"]/p.loc[CITY,"fare_per_occupied_hour"]),
                    "ratio_ci_low":float(np.quantile(ratio,.025)),"ratio_ci_high":float(np.quantile(ratio,.975))})
        completeness.append({"period":period,"days":len(days),"zero_route_day_cells":int((minutes==0).sum())})
    groups["ci_low"]=[cis[(p,r)][0] for p,r in zip(groups.period,groups.route)]
    groups["ci_high"]=[cis[(p,r)][1] for p,r in zip(groups.period,groups.route)]
    return {"unit":"calendar day","replicates":REPLICATES,"seed":SEED,"confidence_level":.95,
            "method":"Percentile bootstrap; same sampled days across all routes within each period; calendar-complete grid with zero-filled missing route/day cells.",
            "completeness":completeness,"comparisons":comparisons,
            "limitation":"Captures within-period day variation, not unseen-season risk, serial dependence, driver clustering or causal uncertainty."}

def chart_outputs(groups,hourly,monthly,quality):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.spines.top":False,"axes.spines.right":False,
                         "axes.titleweight":"bold","axes.edgecolor":"#CBD5E1","text.color":"#183B42"})
    colors={CITY:"#737A82","LaGuardia → Manhattan":"#376B70","JFK → Manhattan":"#995D13"}
    folder=OUT/"charts";folder.mkdir(exist_ok=True)
    fig,ax=plt.subplots(figsize=(10.6,5))
    pos=np.arange(3)
    for offset,period,alpha,label in [(-.17,"train",.5,"Q1 2025 · training"),(.17,"holdout",1,"April 2025 · holdout")]:
        g=groups[groups.period==period].set_index("route").loc[ROUTES]
        vals=g.fare_per_occupied_hour.to_numpy()
        ax.bar(pos+offset,vals,.3,label=label,color=[colors[r] for r in ROUTES],alpha=alpha)
        ax.errorbar(pos+offset,vals,yerr=np.array([vals-g.ci_low.to_numpy(),g.ci_high.to_numpy()-vals]),fmt="none",color="#183B42",capsize=3)
        for x,y in zip(pos+offset,vals):ax.text(x,y+3,f"${y:.1f}",ha="center",fontsize=9)
    ax.set_xticks(pos,["Manhattan\n→ Manhattan","LaGuardia\n→ Manhattan","JFK\n→ Manhattan"])
    ax.set_ylabel("Base fare / occupied hour (USD)")
    ax.set_ylim(0,groups.fare_per_occupied_hour.max()*1.3)
    ax.set_title("A larger fare does not settle the operating decision",loc="left",pad=20)
    ax.legend(frameon=False);ax.grid(axis="y",alpha=.13)
    fig.text(.07,.02,"Ratio of total base fare to occupied time | 95% paired-day bootstrap intervals | idle/repositioning time unavailable",fontsize=8,color="#64748B")
    fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(folder/"01_route_holdout.png",dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10.6,4.8))
    for route in ROUTES:
        h=hourly[(hourly.period=="holdout")&(hourly.route==route)].sort_values("hour")
        values=h.fare_per_occupied_hour.where(h.trips>=100)
        ax.plot(h.hour,values,label=route,color=colors[route],linewidth=2)
    ax.set_xticks(range(0,24,2));ax.set_xlabel("Pickup hour · New York local time");ax.set_ylabel("Base fare / occupied hour (USD)")
    ax.set_title("Time of day changes the comparison",loc="left",pad=18);ax.legend(frameon=False);ax.grid(alpha=.15)
    fig.text(.07,.02,"April 2025 | destination Manhattan | hours with fewer than 100 trips omitted | not a full-shift forecast",fontsize=8,color="#64748B")
    fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(folder/"02_hourly_holdout.png",dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10.6,4.8))
    h=groups[groups.period=="holdout"].set_index("route")
    extra=np.arange(0,61)
    for route in ROUTES:
        row=h.loc[route]
        vals=60*row.fare_usd/(row.occupied_minutes+row.trips*extra)
        ax.plot(extra,vals,color=colors[route],label=route,linewidth=2)
    ax.set_xlabel("Assumed unobserved minutes added per trip");ax.set_ylabel("Base fare / total assumed hour (USD)")
    ax.set_title("Unobserved time can erase an apparent advantage",loc="left",pad=18);ax.legend(frameon=False);ax.grid(alpha=.15)
    fig.text(.07,.02,"Scenario only: each curve applies the x-axis assumption to its own route | not measured queue time, earnings or profit",fontsize=8,color="#64748B")
    fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(folder/"03_extra_time_scenario.png",dpi=170);plt.close(fig)

def run():
    OUT.mkdir(exist_ok=True)
    processed=ROOT/"data"/"processed";processed.mkdir(exist_ok=True)
    manifest=json.loads((ROOT/"data"/"source_manifest.json").read_text(encoding="utf-8"))
    con=duckdb.connect(str(processed/"taxi.duckdb"))
    con.execute("SET threads=4");con.execute("SET memory_limit='2GB'")
    raw=(ROOT/"data"/"raw").as_posix().replace("'","''")
    print("Building trip mart from official Parquet files...",flush=True)
    con.execute((ROOT/"sql"/"01_trip_mart.sql").read_text(encoding="utf-8").replace("{{RAW}}",raw))
    print("Computing cohort and route aggregates...",flush=True)
    source_count=con.execute("SELECT count(*) FROM trips").fetchone()[0]
    expected=sum(x["rows"] for x in manifest["files"] if x["file"].endswith(".parquet"))
    zone_unique=con.execute("SELECT count(*)=count(DISTINCT LocationID) FROM zones").fetchone()[0]
    waterfall=con.execute("SELECT cohort_status,count(*) AS trips FROM trips GROUP BY 1 ORDER BY 1").df()
    eligible_count=con.execute("SELECT count(*) FROM eligible_trips").fetchone()[0]
    study_count=con.execute("SELECT count(*) FROM comparison_trips").fetchone()[0]
    checks={"source_row_count_matches_manifest":source_count==expected,"zone_lookup_unique":bool(zone_unique),
            "waterfall_reconciles":int(waterfall.trips.sum())==source_count,
            "three_study_routes":con.execute("SELECT count(DISTINCT route)=3 FROM comparison_trips").fetchone()[0],
            "positive_study_duration":con.execute("SELECT min(duration_minutes)>=1 AND max(duration_minutes)<=180 FROM comparison_trips").fetchone()[0],
            "no_dst_transition_records":con.execute("SELECT count(*)=0 FROM eligible_trips WHERE pickup_date=DATE '2025-03-09' OR CAST(dropoff_at AS DATE)=DATE '2025-03-09'").fetchone()[0]}
    if not all(checks.values()):raise AssertionError(checks)
    groups=summarize(con,["period","route"])
    groups["eligible_for_ranking"]=groups.trips>=1000
    hourly=summarize(con,["period","route","hour"])
    hourly["eligible_for_ranking"]=hourly.trips>=1000
    monthly=summarize(con,["month","route"])
    daily=summarize(con,["period","pickup_date","route"])
    daily.to_csv(OUT/"daily.csv",index=False)
    bootstrap=paired_day_bootstrap(daily,groups)
    groups["rank"]=groups.groupby("period").fare_per_occupied_hour.rank(method="min",ascending=False).astype(int)
    groups.to_csv(OUT/"groups.csv",index=False);hourly.to_csv(OUT/"hourly.csv",index=False);monthly.to_csv(OUT/"monthly.csv",index=False)
    broad=summarize(con,["period","route"],"broad_eligible AND route <> 'Other routes'")
    broad["rank"]=broad.groupby("period").fare_per_occupied_hour.rank(method="min",ascending=False).astype(int)
    broad.to_csv(OUT/"sensitivity_broad.csv",index=False)
    broad_rows=[]
    for row in broad.to_dict("records"):
        original=groups[(groups.period==row["period"])&(groups.route==row["route"])].iloc[0]
        broad_rows.append({**row,"primary_rate":original.fare_per_occupied_hour,"primary_rank":int(original["rank"]),
                           "rate_change_pct":100*(row["fare_per_occupied_hour"]/original.fare_per_occupied_hour-1)})
    train=groups[groups.period=="train"].set_index("route");hold=groups[groups.period=="holdout"].set_index("route")
    holdout_rows=[{"route":route,"train_rate":train.loc[route,"fare_per_occupied_hour"],"holdout_rate":hold.loc[route,"fare_per_occupied_hour"],
                   "change_pct":100*(hold.loc[route,"fare_per_occupied_hour"]/train.loc[route,"fare_per_occupied_hour"]-1),
                   "train_rank":int(train.loc[route,"rank"]),"holdout_rank":int(hold.loc[route,"rank"])} for route in ROUTES]
    holdout={"training_winner":train.fare_per_occupied_hour.idxmax(),"holdout_winner":hold.fare_per_occupied_hour.idxmax(),
             "ranking_preserved":all(x["train_rank"]==x["holdout_rank"] for x in holdout_rows),"minimum_group_trips":1000,
             "groups":holdout_rows,"interpretation":"Temporal stability check of three predefined route groups; not a randomized experiment or driver-level revenue forecast."}
    be=[];scenario=[]
    for period in ["train","holdout"]:
        g=groups[groups.period==period].set_index("route")
        for route in ROUTES:
            row=g.loc[route];extra=10 if route==CITY else 30
            scenario.append({"period":period,"route":route,"assumed_extra_minutes":extra,
                             "scenario_fare_per_hour":scenario_rate(row.fare_usd,row.occupied_minutes,row.trips,extra)})
            if route!=CITY:
                for city_extra in [0,10,20]:
                    city=g.loc[CITY];city_rate=scenario_rate(city.fare_usd,city.occupied_minutes,city.trips,city_extra)
                    be.append({"period":period,"route":route,"city_extra_minutes":city_extra,
                               "airport_extra_minutes":break_even_minutes(row.mean_fare_usd,row.mean_minutes,city_rate)})
    pd.DataFrame(be).to_csv(OUT/"break_even_scenarios.csv",index=False)
    pd.DataFrame(scenario).to_csv(OUT/"default_scenario.csv",index=False)
    # A lightweight collision audit uses all fields retained in the mart; no row is removed.
    # Equal selected fields do not prove duplicate physical journeys, since IDs are absent.
    print("Checking repeated selected-field signatures...",flush=True)
    repeated=con.execute("""SELECT coalesce(sum(n-1),0) FROM (
      SELECT count(*) AS n FROM comparison_trips
      GROUP BY source_month,pickup_at,dropoff_at,pickup_zone_id,dropoff_zone_id,
               payment_type,rate_code,trip_distance,fare_amount HAVING count(*)>1)""").fetchone()[0]
    quality={"checks":checks,"all_checks_passed":True,"source_trips":source_count,"eligible_trips":eligible_count,
             "study_trips":study_count,"other_clean_route_trips":eligible_count-study_count,
             "waterfall":waterfall.to_dict("records"),
             "raw_missing_zone_lookup_records":con.execute("SELECT count(*) FROM trips WHERE pickup_borough IS NULL OR dropoff_borough IS NULL").fetchone()[0],
             "study_repeated_selected_field_excess_records":int(repeated),
             "deduplication":"No records deduplicated: there is no stable public trip ID. Selected-field repeated signatures are an audit flag, not proof of duplicated journeys.",
             "dst_policy":"Exclude any trip with pickup OR dropoff local date 2025-03-09 to avoid spring clock-change duration ambiguity. Other durations use local wall-clock elapsed seconds.",
             "primary_filters":{"payment_type":[1,2],"rate_code":[1,2],"duration_minutes":"1 <= minutes <= 180",
                 "trip_distance":"0 < miles <= 100","fare_amount":"0 < USD <= 500","zone":"both boroughs known, not Unknown/N/A","month":"pickup month matches source file"},
             "waterfall_note":"Mutually exclusive first-failure labels in SQL order; a record with several issues is counted only once."}
    checks["group_trips_reconcile"]=int(groups.trips.sum())==study_count
    checks["daily_trips_reconcile"]=int(daily.trips.sum())==study_count
    checks["broad_contains_primary"]=all(int(broad[(broad.period==r.period)&(broad.route==r.route)].iloc[0].trips)>=r.trips for r in groups.itertuples())
    if not all(checks.values()):raise AssertionError(checks)
    metrics={"project":"NYC Taxi Shift Economics","schema_version":"1.0.0","generated_at_utc":datetime.now(timezone.utc).isoformat(),
             "source":{"name":manifest["dataset"],"url":manifest["source_page"],"dictionary":manifest["dictionary"],"terms":manifest["terms"]},
             "cohort":{"start":"2025-01-01","end_exclusive":"2025-05-01","train_start":"2025-01-01","train_end_exclusive":"2025-04-01",
                       "holdout_start":"2025-04-01","holdout_end_exclusive":"2025-05-01","timezone":"America/New_York","unit":"reported trip record"},
             "kpis":{"source_trips":source_count,"eligible_trips":eligible_count,"study_trips":study_count,
                      "study_fare_usd":float(groups.fare_usd.sum()),"study_occupied_hours":float(groups.occupied_minutes.sum()/60)},
             "metric_definition":"60 × sum(fare_amount) / sum(occupied minutes). Base fare excludes tips, tolls and surcharges. Occupied time excludes queueing, empty driving and other unobserved time.",
             "groups":groups.to_dict("records"),"hourly":hourly.to_dict("records"),"monthly":monthly.to_dict("records"),
             "quality":quality,"holdout":holdout,"bootstrap":bootstrap,
             "sensitivity":{"broad_filters":"duration > 0 and <= 240 minutes; fare > 0 and <= 1000 USD; all other primary filters unchanged.",
                            "groups":broad_rows,"ranking_preserved":all(r["rank"]==r["primary_rank"] for r in broad_rows)},
             "scenarios":{"default_city_extra_minutes":10,"default_airport_extra_minutes":30,"default_rows":scenario,
                          "break_even":be,"note":"Assumptions, not observed queue/repositioning time. Negative break-even means the airport already trails the city at zero extra airport minutes. No operating cost is subtracted."},
             "caveats":["This is base fare per occupied hour, not driver earnings, net revenue, profit or full-shift productivity.",
                         "The three route groups differ in trip distance, fare rules, hour mix, traffic and selection; group differences are not causal effects.",
                         "Cash tips are unobserved; tips and all surcharges are deliberately outside the metric.",
                         "Card/cash and ratecodes 1/2 only; Flex Fare and negotiated/other fare records are outside scope.",
                         "January–April 2025 is one season. The April holdout is a descriptive persistence check, not proof of future performance.",
                         "TLC is a reporting dataset; errors remain possible. No stable driver, shift or trip identifier is available in these extracts."]}
    save_json("quality_report.json",quality);save_json("metrics.json",metrics)
    waterfall.to_csv(OUT/"quality_waterfall.csv",index=False)
    chart_outputs(groups,hourly,monthly,quality)
    con.close()
    print(json.dumps(safe({"kpis":metrics["kpis"],"groups":metrics["groups"],"holdout":holdout,"sensitivity":metrics["sensitivity"],"quality":quality}),indent=2,ensure_ascii=False))
    return metrics

if __name__=="__main__":run()
