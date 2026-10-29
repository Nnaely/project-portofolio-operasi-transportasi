# Metodologi analisis

## Pertanyaan dan batas keputusan

Analisis menilai apakah perjalanan bandara ke Manhattan layak diteliti lebih lanjut sebagai strategi penempatan taksi, dibandingkan perjalanan yang berawal dan berakhir di Manhattan. Tarif dasar dibagi waktu membawa penumpang, kemudian diperiksa bagaimana asumsi waktu antre dan perjalanan kosong mengubah perbandingan.

Tarif dasar per jam terisi belum mencakup satu shift penuh. Data publik tidak mengidentifikasi shift pengemudi, waktu antre, perjalanan kosong, seluruh tip, maupun biaya operasi. Keluaran proyek berupa perbandingan historis dan rencana pengukuran sebelum pilot operasional.

## Sumber dan reproduksibilitas

Input adalah empat berkas bulanan resmi NYC TLC Yellow Taxi, Januari-April 2025, dan Taxi Zone Lookup Table resmi. Tautannya berasal dari [halaman TLC](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page). Catatan berasal dari penyedia teknologi; TLC tidak menjamin keakuratannya. Manifest `data/source_manifest.json` mengikat analisis pada versi unduhan tertentu melalui ukuran, jumlah baris, URL, dan SHA-256.

Interpretasi kolom mengikuti [kamus resmi tanggal 18 Maret 2025](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf). Kode pembayaran 0 berarti Flex Fare. Tip tunai tidak tercatat. CBD congestion fee adalah biaya terpisah yang mulai berlaku pada 5 Januari 2025.

CSV di `data/raw/` adalah ekspor lengkap semua nilai sumber, dibagi maksimal satu juta baris per bagian. Konversi format tidak menerapkan aturan analisis. Manifest `data/raw_csv_manifest.json` mencatat tipe data dan pemeriksaan tiap bagian. Analisis tetap memakai Parquet untuk efisiensi.

## Populasi dan rute

Satu baris sumber mewakili satu perjalanan yang dilaporkan. Nama berkas bulanan belum membuktikan tanggal perjalanan: bulan pickup harus cocok dengan bulan sumber. Tidak dilakukan deduplikasi tanpa ID perjalanan publik yang stabil.

| Rute | Pickup | Drop-off |
|---|---|---|
| JFK ke Manhattan | Zona 132 | Zona dengan `Borough = Manhattan` pada referensi |
| LaGuardia ke Manhattan | Zona 138 | Zona dengan `Borough = Manhattan` pada referensi |
| Manhattan ke Manhattan | Zona dengan `Borough = Manhattan` | Zona dengan `Borough = Manhattan` |

Ini kelompok geografis. Data tidak menunjukkan niat pengemudi menuju bandara, perjalanan sebelumnya, atau tujuan penumpang berikutnya. Kunci referensi zona harus unik agar join tidak menggandakan baris. Lokasi tak dikenal tidak dianggap Manhattan.

## Aturan kelayakan utama

- Pickup sesuai bulan sumber dan berada dalam Januari-April 2025.
- Pembayaran kartu kredit atau tunai (`payment_type` 1 atau 2).
- Kode tarif standar atau JFK (`RatecodeID` 1 atau 2).
- Durasi 1-180 menit.
- Jarak lebih dari 0 hingga 100 mil.
- Tarif dasar lebih dari USD 0 hingga USD 500.
- Pickup dan drop-off memiliki borough yang dikenali.
- Pickup maupun drop-off tidak jatuh pada 9 Maret 2025.

Batas tersebut adalah pilihan ruang lingkup dan kewajaran yang dinyatakan sejak awal. Baris yang dikeluarkan belum tentu salah. Jumlah penumpang yang kosong tidak otomatis membuat tarif dan durasi tidak dapat digunakan.

Timestamp dibaca sebagaimana waktu lokal NYC dicatat sumber, tanpa konversi ke WIB. Tanggal 9 Maret dikeluarkan secara konservatif karena perpindahan daylight-saving time dapat membuat selisih timestamp tanpa zona waktu menyimpang satu jam. Pilihan ini juga mengeluarkan perjalanan valid pada tanggal tersebut.

Setiap baris mendapat **aturan pertama yang gagal** dalam waterfall pengecualian. Karena itu, jumlah kategori pengecualian dan baris layak kembali tepat ke jumlah sumber. Kategori tersebut bukan jumlah independen semua pelanggaran.

Dari 15.168.579 baris sumber, terdapat 11.044.733 baris layak di seluruh rute yang dikenali. Sebanyak 10.148.555 masuk tiga rute penelitian. Pengecualian pertama terbesar adalah 3.448.522 baris di luar lingkup kartu/tunai; ini tidak berarti seluruhnya merupakan perjalanan keliru.

## Metrik utama dan penyebut

**Tarif dasar per jam terisi = jumlah `fare_amount` / jumlah menit terisi x 60.**

Tarif dasar tidak memasukkan tip, tol, pajak, biaya bandara, maupun biaya tambahan kemacetan. Menit terisi adalah waktu pickup sampai drop-off. Kendaraan berhenti ketika meter aktif tetap berada dalam interval ini.

Rasio jumlah memberi bobot setara untuk setiap menit terisi. Rata-rata rasio tiap perjalanan memberi bobot setara untuk setiap perjalanan, sehingga perjalanan sangat pendek bisa mendominasi. Contoh: tarif USD 20 selama 10 menit dan USD 20 selama 50 menit menghasilkan USD 40 untuk satu jam total. Rata-rata rasio keduanya menghasilkan USD 72/jam dan menjawab pertanyaan berbeda.

Untuk menggabungkan bulan atau kelompok, jumlahkan tarif dan menit dahulu lalu hitung ulang rasionya. Tampilkan rata-rata tarif dan durasi sebagai penjelas, tanpa mengganti metrik utama.

## Pemisahan waktu dan ketidakpastian

Januari-Maret membentuk perbandingan awal; April menjadi pembanding waktu berikutnya. Label `train` dan `holdout` menandai pemisahan waktu deskriptif, bukan model prediksi. Peringkat dilaporkan untuk kelompok dengan minimal 1.000 perjalanan; seluruh enam kelompok rute/periode melampaui batas ini. Batas tersebut merupakan aturan pelaporan, bukan jaminan kekuatan statistik.

Bootstrap mengambil ulang hari kalender dan memakai pilihan hari yang sama untuk seluruh rute. Terdapat 89 tanggal Q1 setelah tanggal DST dikeluarkan dan 30 tanggal April. Hari/rute tanpa perjalanan diisi nol, bukan dihapus. Ada 2.000 pengambilan ulang dengan seed `20251014`; batas interval adalah persentil 2,5 dan 97,5.

Pendekatan tersebut mempertahankan sebagian kondisi harian bersama antarrute. Interval tidak memperbaiki kesalahan sumber, pemilihan rute, perbedaan pengemudi yang tidak terukur, atau ketergantungan antarhari. Tidak tersedia ID pengemudi untuk inferensi berkelompok pada pengemudi.

## Pemeriksaan sensitivitas

Filter lebih longgar memakai durasi positif sampai 240 menit dan tarif dasar positif sampai USD 1.000. Aturan lain tetap sama. Urutan rute tetap bertahan. Pemeriksaan ini hanya menguji dua batas tersebut, bukan seluruh kemungkinan keputusan pembersihan data.

Pada April, tarif dasar per jam terisi adalah USD 83,39 untuk LaGuardia, USD 78,60 untuk JFK, dan USD 64,31 untuk kota. Urutan Q1 bertahan, tetapi tingkat produktivitas ketiganya menurun. Hasil ini menunjukkan konsistensi deskriptif dalam periode studi.

## Skenario waktu tambahan

Untuk `n` perjalanan dan asumsi tambahan `w` menit per perjalanan:

`tarif per jam siklus = 60 x jumlah tarif dasar / (jumlah menit terisi + n x w)`

Asumsi kota dan bandara dipisahkan. Menit tambahan menyatukan waktu antre, idle, dan perjalanan kosong yang dialokasikan per perjalanan; nilainya tidak diukur dalam dataset. Komposisi perjalanan, tarif, dan durasi terisi tetap ditahan. Kondisi permintaan, persaingan pengemudi, dan kemacetan di dunia nyata dapat ikut berubah ketika perilaku berubah.

Ambang waktu tambahan bandara yang menyamai skenario kota:

`60 x rata-rata tarif bandara / tarif per jam skenario kota - rata-rata menit terisi bandara`

Ambang negatif berarti rute bandara sudah tertinggal pada nol menit tambahan. Ambang positif adalah toleransi dalam asumsi, tanpa memasukkan biaya operasi.

Dengan observasi April dan **10 menit tambahan kota**, ambang LaGuardia adalah **41,61 menit** dan JFK **64,17 menit** per perjalanan. Jika bandara mendapat **30 menit tambahan**, hasilnya LaGuardia **USD 42,54**, JFK **USD 50,38**, dan kota **USD 35,76** per jam siklus. Urutan dua bandara berubah karena asumsi waktu tersebut. Angka 10/30 menit hanyalah ilustrasi.

Dokumen membulatkan angka untuk dibaca. Perhitungan memakai total yang belum dibulatkan di `outputs/metrics.json`, `groups.csv`, `default_scenario.csv`, dan `break_even_scenarios.csv`.

## Memisahkan bukti dan asumsi

| Kategori | Isi |
|---|---|
| Teramati | Timestamp, lokasi, jarak, tarif, kode pembayaran/tarif, ringkasan dan pengecualian. |
| Pilihan analis | Periode, ambang kelayakan, definisi rute, minimal sampel, dan prosedur bootstrap. |
| Asumsi skenario | Menit tambahan dan komposisi tarif/durasi yang ditahan tetap. |
| Belum diketahui | Antrean sebenarnya, produktivitas shift lengkap, pendapatan bersih, laba, dampak kausal, dan penerapan langsung ke Indonesia. |

[Rencana pilot](EXPERIMENT_PLAN.md) menjelaskan data baru yang dibutuhkan. Belum ada pilot operasional yang dijalankan untuk proyek portofolio ini. Ketentuan dan atribusi sumber dijelaskan di [ATRIBUSI_ID.md](../ATRIBUSI_ID.md).
