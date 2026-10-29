"""Ekspor seluruh baris Parquet sumber ke CSV tanpa pembersihan atau penyaringan.

Setiap bagian maksimal 1.000.000 baris data, ditambah satu header.
Jalankan dari folder mana saja: python scripts/export_raw_csv.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "data" / "raw_csv_manifest.json"
ROWS_PER_PART = 1_000_000


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def export():
    source_manifest = json.loads((ROOT / "data/source_manifest.json").read_text(encoding="utf-8"))
    old = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    previous = {p["file"]: p["sha256"] for p in old.get("parts", [])}
    con = duckdb.connect()
    con.execute("SET threads=1")
    con.execute("SET preserve_insertion_order=true")
    parts, sources = [], []
    for item in source_manifest["files"]:
        if not item["file"].endswith(".parquet"):
            continue
        source = RAW / item["file"]
        if sha256(source) != item["sha256"]:
            raise ValueError(f"Hash sumber berbeda: {source}. Sumber tidak ditimpa; periksa dahulu.")
        relation = f"read_parquet({literal(source.as_posix())})"
        schema = con.execute(f"DESCRIBE SELECT * FROM {relation}").fetchall()
        columns = {r[0]: r[1] for r in schema}
        count = con.execute(f"SELECT count(*) FROM {relation}").fetchone()[0]
        if count != item["rows"]:
            raise ValueError(f"Jumlah baris sumber berbeda: {source}")
        column_sql = ", ".join('"' + c.replace('"', '""') + '"' for c in columns)
        types_sql = "{" + ", ".join(literal(k) + ": " + literal(v) for k, v in columns.items()) + "}"
        source_parts = []
        for index in range(math.ceil(count / ROWS_PER_PART)):
            offset = index * ROWS_PER_PART
            expected_rows = min(ROWS_PER_PART, count - offset)
            name = f"{source.stem}_part{index + 1:02d}.csv"
            output = RAW / name
            if output.exists() and sha256(output) != previous.get(name):
                raise FileExistsError(f"CSV yang belum dikenali atau telah diedit: {output}. Simpan salinannya sebelum ekspor ulang.")
            query = f"SELECT * FROM {relation} LIMIT {expected_rows} OFFSET {offset}"
            temporary = output.with_suffix(".csv.part")
            con.execute(f"COPY ({query}) TO {literal(temporary.as_posix())} (FORMAT CSV, HEADER true, DELIMITER ',', NULL '')")
            csv_relation = f"read_csv({literal(temporary.as_posix())}, header=true, auto_detect=false, columns={types_sql}, nullstr='', allow_quoted_nulls=false)"
            fingerprint = f"count(*), sum(hash({column_sql})::HUGEINT)"
            before = con.execute(f"SELECT {fingerprint} FROM ({query})").fetchone()
            after = con.execute(f"SELECT {fingerprint} FROM {csv_relation}").fetchone()
            with temporary.open(newline="", encoding="utf-8") as stream:
                header = next(csv.reader(stream))
            if before != after or after[0] != expected_rows or header != list(columns):
                raise ValueError(f"Validasi CSV gagal: {name}; file final tidak diganti.")
            temporary.replace(output)
            part = {"file": name, "source_file": source.name, "part": index + 1,
                    "rows": expected_rows, "source_row_start": offset + 1,
                    "source_row_end": offset + expected_rows, "bytes": output.stat().st_size,
                    "sha256": sha256(output), "roundtrip_count_and_row_fingerprint_match": True}
            parts.append(part)
            source_parts.append(name)
            print(json.dumps({"csv": name, "rows": expected_rows, "verified": True}), flush=True)
        sources.append({"file": source.name, "sha256": item["sha256"], "rows": count,
                        "columns": columns, "csv_parts": source_parts})
    manifest = {"description": "Seluruh baris dan kolom sumber, tanpa filter, join, deduplikasi, atau agregasi.",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "encoding": "UTF-8", "delimiter": ",", "decimal_separator": ".",
                "null_representation": "Sel kosong tanpa kutip; string kosong ditulis dengan kutip.",
                "timestamp_note": "Waktu lokal sebagaimana dicatat sumber; tanpa konversi zona waktu.",
                "rows_per_part_limit": ROWS_PER_PART, "total_trip_rows": sum(p["rows"] for p in parts),
                "csv_bytes": sum(p["bytes"] for p in parts), "sources": sources, "parts": parts}
    assert manifest["total_trip_rows"] == sum(s["rows"] for s in sources)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"parts": len(parts), "rows": manifest["total_trip_rows"], "bytes": manifest["csv_bytes"]}), flush=True)


if __name__ == "__main__":
    export()
