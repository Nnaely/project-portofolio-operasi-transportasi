"""Download the four official NYC TLC Yellow Taxi monthly Parquet files and zone lookup."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/"data"/"raw"
URLS={f"yellow_tripdata_2025-{m:02d}.parquet":f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-{m:02d}.parquet" for m in range(1,5)}
URLS["taxi_zone_lookup.csv"]="https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def fetch(item):
    filename,url=item
    path=RAW/filename
    if not path.exists():
        temporary=path.with_suffix(path.suffix+".part")
        request=urllib.request.Request(url,headers={"User-Agent":"NYC-Taxi-Portfolio/1.0"})
        with urllib.request.urlopen(request,timeout=180) as response,temporary.open("wb") as out:
            while chunk:=response.read(1024*1024):out.write(chunk)
        temporary.replace(path)
    if path.suffix==".parquet":
        with path.open("rb") as f:
            assert f.read(4)==b"PAR1",f"Invalid Parquet: {filename}"
    return {"file":filename,"url":url,"bytes":path.stat().st_size,"sha256":sha256(path),
            "retrieved_at_utc":datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat()}

def download():
    RAW.mkdir(parents=True,exist_ok=True)
    manifest_path=ROOT/"data"/"source_manifest.json"
    previous=json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    expected={item["file"]:item["sha256"] for item in previous.get("files",[])}
    with ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(fetch,URLS.items()))
    changed=[item["file"] for item in files if item["file"] in expected and item["sha256"]!=expected[item["file"]]]
    if changed:
        raise RuntimeError("Source bytes differ from the saved portfolio manifest: "+", ".join(changed)+". The original manifest was preserved. Review the publisher revision before intentionally refreshing this study.")
    import duckdb
    con=duckdb.connect()
    for item in files:
        path=RAW/item["file"]
        if path.suffix==".parquet":item["rows"]=con.execute("SELECT count(*) FROM read_parquet(?)",[str(path)]).fetchone()[0]
        else:
            with path.open(newline="",encoding="utf-8-sig") as f:item["rows"]=sum(1 for _ in csv.DictReader(f))
    manifest={"dataset":"NYC TLC Yellow Taxi Trip Records, January–April 2025","publisher":"NYC Taxi & Limousine Commission",
              "source_page":"https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page",
              "dictionary":"https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf",
              "terms":"https://www.nyc.gov/home/terms-of-use.page",
              "retrieved_at_utc":datetime.now(timezone.utc).isoformat(),"files":files,
              "version_note":"TLC monthly files have no immutable version label. SHA256 hashes pin the exact downloaded bytes; future source revisions may change results.",
              "redistribution":"Raw Parquet and row-level derived files are omitted from the portable portfolio package."}
    (ROOT/"data"/"source_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"files":files},indent=2))
    return manifest

if __name__=="__main__":download()
