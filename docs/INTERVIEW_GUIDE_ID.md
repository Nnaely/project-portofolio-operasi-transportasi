# Panduan presentasi dan latihan kepemilikan

*Documentation by Nakata - Making this study easier to understand.*

Proyek ini adalah studi portofolio independen memakai data publik NYC. Jangan mengaku bekerja untuk TLC, menjalankan pilot, meningkatkan pendapatan pengemudi, atau menemukan waktu antre yang sebenarnya. Nilai proyek terletak pada ketepatan pertanyaan, denominator, dan batas keputusan.

## Pitch sekitar 90 detik

“Saya menguji pertanyaan operasional yang terlihat sederhana: apakah perjalanan dari bandara lebih produktif daripada perjalanan dalam kota? Saya memakai data resmi Yellow Taxi NYC Januari–April 2025, dengan rute JFK ke Manhattan, LaGuardia ke Manhattan, dan Manhattan ke Manhattan.

Saya sengaja memakai tarif dasar per jam membawa penumpang. Menghitung rata-rata tarif per perjalanan akan mengabaikan durasi, sedangkan menyebut hasilnya pendapatan pengemudi akan mengabaikan waktu antre, perjalanan kosong, dan biaya.

Saya membangun pipeline SQL dengan aturan kelayakan dan laporan pengecualian, memakai Januari–Maret sebagai periode kalibrasi dan April sebagai pembanding berikutnya. Pada April, tarif dasar per jam membawa penumpang sekitar 83 dolar untuk LaGuardia, 79 dolar untuk JFK, dan 64 dolar untuk perjalanan dalam Manhattan.

Bagian keputusan menggunakan skenario: berapa menit tambahan tanpa penumpang yang akan menghapus keunggulan tarif per jam sebuah rute? Angka menit tersebut adalah asumsi dan ambang impas, bukan hasil observasi antrean. Output akhirnya adalah dashboard, analisis yang bisa diulang, serta rancangan pengukuran shift sebelum strategi operasional diuji.”

## Angka yang dapat Anda telusuri ke output

| Fakta / skenario | Hasil pada build ini | Batas interpretasi |
|---|---|---|
| Ukuran sumber dan studi | 15.168.579 reported trips dibaca; 10.148.555 masuk tiga rute perbandingan. | Angka studi bukan seluruh trip NYC. Filter card/cash, rate code, lokasi, dan kualitas mempersempit scope. |
| Produktivitas April | LGA USD 83,39; JFK USD 78,60; Manhattan USD 64,31 per jam berpenumpang. | Tidak memasukkan waktu kosong atau biaya. |
| Stabilitas waktu | Urutan LGA > JFK > Manhattan tetap pada April; masing-masing rate menurun dari Q1. | Persistensi deskriptif, bukan bukti strategi berhasil. |
| Skenario 10 menit kota / 30 menit bandara | JFK USD 50,38; LGA USD 42,54; kota USD 35,76 per jam yang dimodelkan. | Urutan bandara berbalik akibat asumsi. Menit tersebut tidak diobservasi. |
| Ambang impas terhadap kota +10 menit | LGA 41,61 menit; JFK 64,17 menit tambahan per trip. | Ini total waktu kosong hipotetis, bukan waktu antre maksimum yang sudah divalidasi. |

Sumber angka: `outputs/metrics.json`, `groups.csv`, `default_scenario.csv`, dan `break_even_scenarios.csv`. Hitung ulang salah satu baris sebelum presentasi; gunakan angka penuh untuk kalkulasi lalu bulatkan hasil untuk penjelasan.

## Pertanyaan yang harus bisa Anda jawab

| Pertanyaan | Hal yang perlu Anda demonstrasikan |
|---|---|
| Mengapa rasio jumlah tarif terhadap jumlah durasi? | Satu perjalanan 1 menit dapat menghasilkan fare/hour ekstrem. Rasio jumlah memberi bobot pada waktu yang benar-benar tercatat. Buat contoh dua perjalanan dan hitung kedua cara. |
| Apa arti satu baris? | Satu reported trip, bukan satu pengemudi atau satu shift. Tidak ada ID pengemudi untuk merekonstruksi aktivitas kosong. |
| Mengapa bukan `total_amount`? | Total mencampur tarif, tips tercatat, dan biaya tambahan. Tarif dasar dipilih untuk perbandingan yang jelas; keduanya bukan laba. |
| Apakah tip nol berarti penumpang tidak memberi tip? | Tidak. Tips tunai tidak masuk field sumber. |
| Apa arti payment code 0? | Flex Fare menurut kamus resmi 2025. Ia dikeluarkan dari scope card/cash; jangan menyebutnya data hilang. |
| Bagaimana mendefinisikan bandara? | Pickup zone 132 atau 138, lalu drop-off harus masuk borough Manhattan pada lookup. Bukan mencari kata airport pada komentar. |
| Apakah join menggandakan trips? | Lookup `LocationID` harus unik. Lookup dipakai dua kali dengan peran pickup dan drop-off; jumlah baris harus tetap. |
| Mengapa data dalam file Januari bisa dikeluarkan? | Pickup harus sesuai bulan file dan rentang analisis. Nama file tidak menjamin seluruh isi tanggalnya benar. |
| Bagaimana menangani DST? | Perjalanan yang pickup atau drop-off pada 9 Maret 2025 dikeluarkan secara eksplisit agar selisih jam lokal tidak diperlakukan sebagai elapsed time yang pasti. |
| Apa arti interval bootstrap? | Stabilitas perbandingan terhadap variasi hari pada periode ini. Ia tidak mengatasi pemilihan rute, seluruh ketergantungan waktu, atau kualitas sumber. |
| Apakah April membuktikan strategi berhasil? | Tidak. April mengecek persistensi perbandingan deskriptif, bukan efek mengirim pengemudi ke bandara. |
| Apa yang bisa membalik kesimpulan? | Waktu kosong dan biaya bandara; perubahan campuran jam/rute; persaingan antar pengemudi; perbedaan aturan filter. |

## Satu minggu untuk benar-benar menguasai proyek

| Hari | Tugas mandiri | Bukti penguasaan |
|---|---|---|
| 1 | Baca kamus resmi dan telusuri satu file Parquet serta lookup. | Jelaskan fare, tip, fee, lokasi, dan waktu tanpa mencampurkannya. |
| 2 | Jalankan pipeline sesuai README; baca seluruh quality waterfall. | Cocokkan jumlah eligible + seluruh alasan pengecualian dengan jumlah input. |
| 3 | Tulis ulang query tiga rute dan rasio tarif per jam tanpa menyalin. | Angka sesuai hasil utama; jelaskan mengapa join tidak boleh menggandakan baris. |
| 4 | Hitung sendiri rumus skenario dan ambang impas dengan kalkulator. | Mengubah menit tambahan memberi hasil yang sama dengan dashboard. |
| 5 | Bandingkan hasil Q1, April, dan filter yang lebih longgar. | Jelaskan hasil yang berubah maupun tetap, tanpa memilih hanya hasil yang mendukung cerita. |
| 6 | Pelajari bootstrap per hari dan rencana pilot. | Jelaskan mengapa jutaan trip tidak berarti jutaan observasi independen. |
| 7 | Rekam demo 3–5 menit; minta orang lain mencari satu klaim terlalu jauh. | Anda dapat membedakan temuan data, pilihan analisis, asumsi, dan hal yang belum diketahui. |

## Alur demo

Mulai dengan pertanyaan, tampilkan April, lalu bandingkan tarif dan durasi. Ubah asumsi waktu tambahan dan jelaskan titik perpotongan. Tunjukkan satu query inti dan satu pengecualian kualitas yang material. Akhiri dengan data shift apa yang perlu dikumpulkan sebelum pilot.

Jika ditanya penggunaan AI, jelaskan bagian yang dibantu dan verifikasi yang benar-benar Anda lakukan. Contoh: “AI membantu menyusun implementasi awal; saya memeriksa definisi sumber, mereproduksi query utama, dan menghitung ulang skenario.” Jangan mengucapkan bagian verifikasi tersebut sebelum mengerjakannya.

## Kalimat CV setelah Anda menguasai hasil

“Membangun analisis SQL/Python atas data trip publik NYC TLC untuk membandingkan produktivitas tarif dasar rute bandara dan dalam kota, dengan pemisahan waktu kalibrasi/holdout, audit kualitas data, bootstrap per hari, dan skenario waktu kosong yang eksplisit.”

Tambahkan ukuran data terverifikasi dan temuan yang bisa dipertahankan saat wawancara. Hindari klaim profit, uplift, atau pengalaman perusahaan yang tidak terjadi.
