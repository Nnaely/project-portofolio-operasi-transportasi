# Kamus data dan definisi metrik

Nama kolom asli dipertahankan agar cocok dengan sumber, CSV, SQL, dan notebook. Satuan uang adalah USD, jarak mil, dan waktu mengikuti catatan lokal NYC. Definisi resmi tersedia pada [kamus Yellow Taxi](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf).

## Seluruh kolom CSV perjalanan

| Kolom | Arti dan penggunaan |
|---|---|
| `VendorID` | Kode penyedia teknologi pelapor; bukan ID pengemudi. |
| `tpep_pickup_datetime` | Waktu mulai perjalanan yang dicatat. Menentukan kelayakan bulan/tanggal. |
| `tpep_dropoff_datetime` | Waktu akhir perjalanan yang dicatat. Selisih terhadap pickup membentuk durasi. |
| `passenger_count` | Jumlah penumpang yang dilaporkan. Nilai hilang tidak otomatis membatalkan tarif/durasi. |
| `trip_distance` | Jarak perjalanan tercatat dalam mil; tidak mencakup seluruh jarak shift. |
| `RatecodeID` | Klasifikasi tarif. Lingkup utama menggunakan 1 standar dan 2 JFK. |
| `store_and_fwd_flag` | Indikator data disimpan sebelum dikirim: Y = disimpan lalu dikirim; N = tidak. |
| `PULocationID` | ID zona pickup; 132 = JFK, 138 = LaGuardia. |
| `DOLocationID` | ID zona drop-off, dipetakan terpisah ke referensi zona. |
| `payment_type` | Kode pembayaran. Lingkup utama: 1 kartu kredit, 2 tunai. Kode 0 berarti Flex Fare. |
| `fare_amount` | Tarif dasar tercatat. Inilah pembilang metrik utama. |
| `extra` | Biaya tambahan lain pada meter; tidak masuk pembilang utama. |
| `mta_tax` | Pajak MTA tercatat; terpisah dari tarif dasar. |
| `tip_amount` | Tip yang tercatat. Tip tunai tidak dicakup. |
| `tolls_amount` | Tol tercatat; terpisah dari tarif dasar. |
| `improvement_surcharge` | Biaya tambahan peningkatan layanan tercatat. |
| `total_amount` | Total tagihan penumpang yang dicatat, tidak mencakup tip tunai. Belum merupakan laba atau pendapatan bersih pengemudi. |
| `congestion_surcharge` | Biaya tambahan kemacetan yang terpisah. |
| `Airport_fee` | Biaya bandara pada sumber studi ini; kapitalisasi dipertahankan. |
| `cbd_congestion_fee` | Biaya kemacetan CBD, berlaku mulai 5 Januari 2025. |

Kolom biaya tambahan, pajak, tip, dan tol tidak dimasukkan ke pembilang tarif dasar. Nilai CSV mentah tidak dibersihkan; angka negatif, nol, atau kosong tetap dapat ditemukan. Tipe asli tiap kolom/periode berada pada `sources[].columns` di `data/raw_csv_manifest.json`.

## Referensi zona

| Kolom | Arti |
|---|---|
| `LocationID` | Kunci zona; harus unik agar join tidak menggandakan perjalanan. |
| `Borough` | Wilayah administratif untuk menentukan Manhattan dan lokasi yang dikenali. |
| `Zone` | Nama zona yang dapat dibaca manusia. |
| `service_zone` | Klasifikasi wilayah layanan dari referensi. |

File `taxi_zone_lookup.csv` memiliki 265 baris. Nama zona tidak mengidentifikasi pengemudi atau rute kendaraan lengkap.

## Kolom hasil transformasi

| Kolom | Arti |
|---|---|
| `pickup_at`, `dropoff_at` | Nama timestamp dalam mart SQL. |
| `pickup_zone_id`, `dropoff_zone_id` | Nama kunci lokasi dalam mart. |
| `rate_code` | Nama `RatecodeID` dalam mart. |
| `source_file`, `source_month` | Berkas dan bulan asal, dipakai memeriksa kecocokan bulan pickup. |
| `pickup_date`, `month`, `hour` | Tanggal, bulan, dan jam pickup yang diturunkan dari timestamp. |
| `pickup_borough`, `dropoff_borough` | Hasil join geografis. |
| `route` | Kelompok rute penelitian atau rute lain. |
| `period` | `train` = Januari-Maret; `holdout` = April. Bukan penanda model prediksi. |
| `cohort_status` | Aturan pertama yang gagal atau `eligible` untuk baris layak. |
| `broad_eligible` | Penanda kelayakan pada filter sensitivitas lebih longgar. |

Kolom turunan ini berada pada hasil analisis; tidak ditambahkan ke CSV mentah.

## Metrik

| Nama | Satuan | Definisi |
|---|---|---|
| `duration_minutes` | Menit | Selisih drop-off dan pickup, setelah aturan tanggal/DST dan kewajaran. |
| `trips` | Perjalanan dilaporkan | Jumlah baris layak dalam kelompok. |
| `fare_usd` | USD | Jumlah `fare_amount` yang layak. |
| `occupied_minutes` | Menit | Jumlah durasi terisi yang layak. |
| `mean_fare_usd` | USD/perjalanan | `fare_usd / trips`. |
| `mean_minutes` | Menit/perjalanan | `occupied_minutes / trips`. |
| `fare_per_occupied_hour` | USD/jam terisi | `60 * fare_usd / occupied_minutes`. |
| Rasio terhadap kota | Kelipatan | Produktivitas rute / produktivitas Manhattan pada periode dan definisi sama. |
| Produktivitas skenario | USD/jam siklus asumsi | `60 * fare_usd / (occupied_minutes + trips * assumed_extra_minutes)`. |
| Waktu tambahan impas | Menit/perjalanan | Waktu tambahan bandara saat produktivitasnya sama dengan skenario kota yang dipilih. |
| `ci_low`, `ci_high` | Mengikuti metrik | Batas interval bootstrap persentil 95%. |

## Satuan baris dan penyebut

Data mentah mempunyai satu baris per perjalanan dilaporkan. Ringkasan rute mempunyai satu baris per periode/rute. Ringkasan harian mempunyai satu baris per tanggal/rute dan dipakai untuk bootstrap berpasangan.

`eligible_trips` mencakup rute lain yang diketahui. `comparison_trips` hanya mencakup tiga rute penelitian. Perjalanan Flex Fare, pembayaran di luar lingkup, kode tarif lain, lokasi tidak dikenal, dan baris yang gagal aturan tidak boleh masuk kembali tanpa sengaja ke penyebut grafik.

Tidak tersedia ID perjalanan yang dijamin unik maupun ID shift pengemudi. Dua baris dengan nilai sama tidak otomatis merupakan kesalahan duplikasi. Hak data mengikuti ketentuan NYC; lihat [atribusi](../ATRIBUSI_ID.md).
