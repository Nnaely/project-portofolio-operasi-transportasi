# Catatan verifikasi

Analisis awal diperiksa 14 Oktober 2026. Penambahan CSV mentah dan dokumen Indonesia diperiksa 15 Oktober 2026. Sumber analisis mengacu pada SHA-256 di `data/source_manifest.json`.

| Pemeriksaan | Hasil |
|---|---|
| Sumber | Lima berkas sumber yang digunakan cocok dengan hash manifest. Empat Parquet berisi 15.168.579 perjalanan. |
| CSV mentah | 17 bagian, maksimal satu juta baris data per bagian. Total 15.168.579 baris, semua 20 kolom sumber dipertahankan. |
| Pemeriksaan tiap CSV | Header, jumlah baris, dan jumlah fingerprint hash nilai baris setelah pembacaan ulang bertipe cocok dengan potongan sumber. SHA-256 tiap CSV dicatat. |
| Referensi zona | CSV resmi 265 baris tersedia di folder yang sama, terpisah dari hitungan perjalanan. |
| Pipeline analisis awal | Sembilan pemeriksaan kualitas lolos, termasuk rekonsiliasi pengecualian, keunikan zona, dan total rute/hari. |
| Uji analitis awal | 11 uji lolos: agregasi, skenario, bulan sumber, DST, join, retensi tanda tangan duplikat, dan lingkup tarif/pembayaran. |
| Notebook awal | Enam sel kode telah dijalankan dan keluarannya disimpan. |
| Notebook Indonesia | Enam sel kode dijalankan ulang; narasi dan pesan penjelas memakai bahasa Indonesia. |
| Web produksi | https://nakata-airport-or-city.vercel.app/ dapat diakses tanpa login; tanda tangan Nakata kecil pada footer. |
| Kontrol web | Pemilihan April menghasilkan 2.678.168 perjalanan pembanding. Skenario nol menit bandara kembali ke tarif dasar per jam terisi bandara. |
| Tampilan web | Desktop dan ponsel diperiksa; tabel lebar menggulir di dalam wadahnya. |
| Ringkasan PDF Indonesia | Tiga halaman dirender untuk pemeriksaan keterbacaan, tata letak, dan ketepatan angka. |
| Paket portofolio | Dokumen Indonesia, kode ekspor, manifest, dan hasil agregat disertakan. Data mentah besar, database, cache, dan identitas/kredensial hosting dikecualikan. |

Ketika menyiapkan ekspor, file Januari lokal ditemukan berbeda dari hash studi dan gagal dibaca DuckDB. File tersebut dipertahankan pada `data/raw/_preserved/`. File resmi Januari diambil ulang dan cocok dengan SHA-256 manifest awal sebelum dipakai untuk CSV. Hasil analisis tetap mengacu pada sumber yang sama dengan studi awal.

Pemeriksaan fingerprint merupakan pemeriksaan integritas praktis dengan kemungkinan benturan hash, bukan pembuktian formal kesetaraan setiap nilai. Pemeriksaan web mencakup kontrol yang disertakan, belum seluruh browser atau teknologi bantu. Keakuratan laporan sumber tetap mengikuti keterbatasan penerbit. Pilot operasional belum dilaksanakan.
