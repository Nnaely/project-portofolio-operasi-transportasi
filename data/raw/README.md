# Data mentah

Empat sumber bulanan NYC TLC menghasilkan 15.168.579 perjalanan. CSV lengkap dibagi menjadi 17 bagian dengan maksimal 1.000.000 baris data per bagian. `taxi_zone_lookup.csv` adalah referensi 265 zona dan disertakan di repo.

## Mengambil seluruh CSV

Unduh [arsip CSV Januari-April 2025](https://github.com/Nnaely/project-portofolio-operasi-transportasi/releases/download/v1.0.0/data-mentah-nyc-tlc-jan-apr-2025.zip), lalu ekstrak **di folder utama repo**. Struktur arsip sudah memakai `data/raw/`, sehingga CSV langsung berada di folder ini. Cocokkan SHA-256 arsip dengan `SHA256SUMS.txt` pada [rilis](https://github.com/Nnaely/project-portofolio-operasi-transportasi/releases/tag/v1.0.0). Tidak ada filter, deduplikasi, atau agregasi pada ekspor mentah.

Alternatif dari sumber resmi:

```text
python scripts/download_data.py
python scripts/export_raw_csv.py
```

Analisis membaca Parquet resmi. Bila hanya mengambil arsip CSV, tetap jalankan pengunduh Parquet sebelum `scripts/analyze.py`. Manifest sumber dan CSV ada di folder `data/`. Panduan impor Excel/Python ada di [panduan data mentah](../../docs/PANDUAN_DATA_MENTAH_ID.md).

Berkas data besar tersedia melalui Releases; riwayat Git menyimpan kode, metadata sumber, dan hasil agregat. Sumber: [NYC TLC](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page).
