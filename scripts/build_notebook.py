"""Create and actually execute the review notebook from saved, auditable aggregates."""
import json
import os
from pathlib import Path
import sys
import tempfile
import nbformat as nbf
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]
nb=nbf.v4.new_notebook()
md=nbf.v4.new_markdown_cell;code=nbf.v4.new_code_cell
nb.cells=[
md("""# Airport fares, occupied time, and the missing operating denominator

**Decision brief:** Should a taxi operator prioritize JFK or LaGuardia pickups to Manhattan over trips within Manhattan? This project first checks what the public trip data can support, then shows how unobserved queueing and empty driving could change the comparison.

**Dataset:** NYC TLC Yellow Taxi, January–April 2025. January–March defines the training comparison; April is a fixed temporal holdout. Reported card/cash trips with fare ratecodes 1/2 only. See `docs/METHODOLOGY.md` for all exclusions.

**Primary metric:** total `fare_amount` divided by total occupied hours. This is neither net revenue nor full-shift earnings. Fare records omit the unobserved operating time and costs needed for either claim.
"""),
code("""from pathlib import Path
import json
import pandas as pd
from IPython.display import display, Image
ROOT = Path.cwd() if (Path.cwd() / 'outputs').exists() else Path.cwd().parent
metrics = json.loads((ROOT / 'outputs/metrics.json').read_text(encoding='utf-8'))
groups = pd.read_csv(ROOT / 'outputs/groups.csv')
display(pd.DataFrame([metrics['kpis']]))"""),
md("""## 1. Establish the cohort before comparing routes

The source has no stable public trip identifier. Records are retained; repeated selected-field signatures are reported rather than silently deduplicated. A unique taxi-zone lookup prevents join fanout. The waterfall uses the first failing rule so counts add back to source rows. March 9 is excluded for trips with pickup or dropoff on the local daylight-saving transition date.
"""),
code("""display(pd.DataFrame(metrics['quality']['waterfall']))
assert metrics['quality']['all_checks_passed']
assert sum(x['trips'] for x in metrics['quality']['waterfall']) == metrics['kpis']['source_trips']
display(pd.DataFrame(metrics['quality']['checks'].items(), columns=['check','passed']))"""),
md("""## 2. Avoid the mean-of-ratios trap

An example: one $20 fare takes 10 minutes and another $20 fare takes 50 minutes. The mean of the two trip-hour rates is $72/hour; the correct total is $40 over 60 minutes, or $40/hour. Aggregation therefore preserves dollars and occupied minutes before dividing.
"""),
code("""display(groups[['period','route','trips','mean_fare_usd','mean_minutes','fare_per_occupied_hour','ci_low','ci_high']].round(2))
display(Image(filename=str(ROOT / 'outputs/charts/01_route_holdout.png')))"""),
md("""## 3. Inspect the predeclared April holdout

Route groups and thresholds were fixed before the April comparison. Confidence intervals come from 2,000 paired daily bootstrap samples: all routes share the same sampled days to preserve common traffic and demand shocks. These intervals describe day variation within the period; they do not remove group selection or estimate a causal advantage.
"""),
code("""display(pd.DataFrame(metrics['holdout']['groups']).round(2))
display(pd.DataFrame(metrics['bootstrap']['comparisons']).round(3))
print('Ranking preserved in April:', metrics['holdout']['ranking_preserved'])
display(Image(filename=str(ROOT / 'outputs/charts/02_hourly_holdout.png')))"""),
md("""## 4. Stress-test the filter choices

The broader sensitivity allows duration over zero through 240 minutes, and positive fares through $1,000. All other scope choices stay fixed. This tests sensitivity to those particular boundaries, not to every possible cleaning decision.
"""),
code("""display(pd.DataFrame(metrics['sensitivity']['groups'])[['period','route','trips','fare_per_occupied_hour','primary_rate','rate_change_pct','rank','primary_rank']].round(2))
print('Ranking preserved under broader limits:', metrics['sensitivity']['ranking_preserved'])"""),
md("""## 5. Make the missing denominator visible

The scenario adds assumed unobserved minutes per trip, separately for airport and city trips. The default of 30 airport minutes and 10 city minutes is illustrative, not measured. The break-even threshold is the maximum airport extra time at which its fare per total assumed hour matches the chosen city scenario; a negative value means it already trails at zero airport extra time.

`scenario rate = 60 × total base fare / (occupied minutes + trips × assumed extra minutes)`

`airport break-even minutes = mean airport fare / city scenario hourly rate × 60 − mean airport occupied minutes`
"""),
code("""display(pd.DataFrame(metrics['scenarios']['default_rows']).round(2))
display(pd.DataFrame(metrics['scenarios']['break_even']).round(2))
display(Image(filename=str(ROOT / 'outputs/charts/03_extra_time_scenario.png')))"""),
md("""## 6. What I would measure before changing dispatch

Use the holdout and scenario as a decision gate, then run the operational pilot in `docs/EXPERIMENT_PLAN.md`. Capture queue minutes, empty driving, completed trips per shift, driver payments, operating costs and cancellations. Compare matched hour/day operating windows, not the highest-fare anecdotes. A route comparison in public trip records cannot establish full-shift profitability.

**Reproduce:** `python scripts/download_data.py`, `python scripts/analyze.py`, `python -m unittest discover -s tests -v`, then `python scripts/build_notebook.py`.

Source URLs, file dates, row counts and SHA256 hashes are in `data/source_manifest.json`. The notebook consumes aggregates; the full transformation is SQL plus a short Python orchestration script.
""")
]
nb.metadata={"kernelspec":{"name":"taxi-portfolio","display_name":"Python (taxi portfolio)","language":"python"},"language_info":{"name":"python","version":sys.version.split()[0]}}
output=ROOT/"notebooks"/"01_route_economics.ipynb"
output.parent.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory() as temp:
    kernel=Path(temp)/"kernels"/"taxi-portfolio";kernel.mkdir(parents=True)
    (kernel/"kernel.json").write_text(json.dumps({"argv":[sys.executable,"-m","ipykernel_launcher","-f","{connection_file}"],"display_name":"Python (taxi portfolio)","language":"python"}),encoding="utf-8")
    previous=os.environ.get("JUPYTER_PATH")
    os.environ["JUPYTER_PATH"]=temp+(os.pathsep+previous if previous else "")
    try:
        NotebookClient(nb,timeout=120,kernel_name="taxi-portfolio",resources={"metadata":{"path":str(ROOT)}}).execute()
    finally:
        if previous is None:os.environ.pop("JUPYTER_PATH",None)
        else:os.environ["JUPYTER_PATH"]=previous
nb.metadata.kernelspec={"name":"python3","display_name":"Python 3","language":"python"}
nbf.write(nb,output)
print(f"Executed {sum(c.cell_type=='code' for c in nb.cells)} cells without errors: {output}")
