"""Bangun ringkasan eksekutif Indonesia dari metrik proyek, tanpa angka rekaan."""
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.graphics.shapes import Drawing, Rect, String, Line

from build_memo import setup_fonts, CREAM, INK, MUTED, LINE, AMBER, MOSS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/RINGKASAN_EKSEKUTIF_ID.pdf"
WIDTH = 507


def number(value, digits=2):
    return f"{value:,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(CREAM)
    canvas.rect(0, 0, 595.2756, 841.8898, fill=1, stroke=0)
    canvas.setFillColor(INK)
    canvas.setFont("Bold", 8)
    canvas.drawString(44, 811, "AIRPORT OR CITY? / NAKATA")
    canvas.setFont("Body", 8)
    canvas.drawRightString(551, 811, "RINGKASAN EKSEKUTIF / 15 OKT 2026")
    canvas.setStrokeColor(LINE)
    canvas.line(44, 798, 551, 798)
    canvas.line(44, 47, 551, 47)
    canvas.setFillColor(MUTED)
    canvas.setFont("Body", 7.5)
    canvas.drawString(44, 31, "Studi independen | NYC TLC Yellow Taxi, Januari-April 2025")
    canvas.drawRightString(551, 31, f"BAHASA INDONESIA / {doc.page:02d}")
    canvas.restoreState()


def main():
    setup_fonts()
    styles = {
        "title": ParagraphStyle("titleID", fontName="Serif", fontSize=27, leading=31, textColor=INK, spaceAfter=15),
        "h": ParagraphStyle("hID", fontName="Bold", fontSize=11, leading=15, textColor=AMBER, spaceBefore=15, spaceAfter=8),
        "body": ParagraphStyle("bodyID", fontName="Body", fontSize=10, leading=14.3, textColor=INK, spaceAfter=10),
        "small": ParagraphStyle("smallID", fontName="Body", fontSize=8.4, leading=11.6, textColor=MUTED, spaceAfter=8),
        "cell": ParagraphStyle("cellID", fontName="Body", fontSize=8.6, leading=12, textColor=INK),
    }
    def p(text, style="body"):
        return Paragraph(text, styles[style])
    def table(rows, widths):
        t = Table([[p(str(x), "cell") for x in row] for row in rows], colWidths=widths, hAlign="LEFT")
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5DDCD")), ("LINEBELOW", (0, 0), (-1, 0), .7, INK), ("LINEBELOW", (0, 1), (-1, -1), .4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9)]))
        return t
    m = json.loads((ROOT / "outputs/metrics.json").read_text(encoding="utf-8"))
    groups = {(g["route"], g["period"]): g for g in m["groups"]}
    routes = sorted({g["route"] for g in m["groups"]}, key=lambda r: 0 if r.startswith("JFK") else 1 if r.startswith("LaGuardia") else 2)
    name = lambda r: r.replace("→", "ke")
    s = [p("01 / KEPUTUSAN YANG PERLU DIUKUR", "h"), p("Tarif lebih besar.<br/>Bagaimana dengan waktunya?", "title"),
         p("Apakah operator taksi perlu mengutamakan perjalanan dari bandara menuju Manhattan dibandingkan perjalanan di dalam Manhattan?"),
         p("<b>Usulan keputusan:</b> ukur waktu operasi satu siklus kendaraan secara lengkap, kemudian uji rekomendasi penempatan melalui pilot. Data perjalanan publik memberikan alasan untuk mengukur; pelaksanaan pilot masih diperlukan."),
         p("APA YANG DITUNJUKKAN APRIL", "h")]
    rows = [["Rute", "Perjalanan", "Tarif dasar rata-rata", "Menit terisi rata-rata", "USD/jam terisi"]]
    for r in [routes[1], routes[0], routes[2]]:
        g=groups[(r,"holdout")]
        rows.append([name(r),number(g["trips"],0),number(g["mean_fare_usd"]),number(g["mean_minutes"]),number(g["fare_per_occupied_hour"])])
    s += [table(rows,[153,79,94,88,93]),Spacer(1,12),
          p("LaGuardia memiliki tarif dasar per jam terisi tertinggi. JFK memiliki tarif rata-rata lebih besar, tetapi waktu membawa penumpangnya juga lebih panjang. Urutan produktivitas Januari-Maret bertahan pada April."),
          p("KONTRAK METRIK", "h"),
          p("<b>Tarif dasar per jam terisi = jumlah fare_amount / jumlah menit terisi x 60.</b> Tarif dan menit dijumlahkan dahulu. Tip, tol, pajak, dan biaya tambahan tidak masuk pembilang."),
          p(f"Sumber: {number(m['kpis']['source_trips'],0)} catatan perjalanan; {number(m['kpis']['eligible_trips'],0)} memenuhi aturan; {number(sum(g['trips'] for g in m['groups']),0)} masuk tiga rute penelitian. Januari-Maret membentuk perbandingan awal; April menjadi pembanding berikutnya.","small"),
          p("Waktu terisi hanya mencakup pickup sampai drop-off. Waktu memperoleh penumpang berikutnya, antre, perjalanan kosong, dan biaya diperlukan untuk menilai satu shift penuh.","small"),PageBreak()]

    s += [p("02 / BUKTI DAN ASUMSI WAKTU", "h"),p("Urutan bertahan.<br/>Keputusan tetap bersyarat.","title")]
    drawing=Drawing(WIDTH,184)
    drawing.add(Rect(0,0,WIDTH,184,fillColor=colors.HexColor("#FCFAF4"),strokeColor=None))
    for label,color,x in [("Jan-Mar",MOSS,15),("April",AMBER,125)]:
        drawing.add(Rect(x,165,8,8,fillColor=color,strokeColor=None));drawing.add(String(x+14,166,label,fontName="Body",fontSize=9,fillColor=MUTED))
    for i,r in enumerate(routes):
        y=132-i*49
        drawing.add(String(15,y-5,name(r),fontName="Body",fontSize=9,fillColor=INK))
        for period,dy,color in [("train",0,MOSS),("holdout",-18,AMBER)]:
            rate=groups[(r,period)]["fare_per_occupied_hour"]
            drawing.add(Rect(178,y+dy,rate/100*252,11,fillColor=color,strokeColor=None))
            drawing.add(String(178+rate/100*252+7,y+dy+2,number(rate),fontName="Body",fontSize=8.5,fillColor=INK))
    s += [drawing,p("Grafik: USD tarif dasar per jam terisi. Ketidakpastian dihitung dengan 2.000 pengambilan ulang hari kalender berpasangan. Perbedaan rute dapat berkaitan dengan komposisi perjalanan, waktu, dan kemacetan.","small"),
          p("TAMBAHKAN WAKTU YANG BELUM TERCATAT", "h"),
          p("Asumsi ilustratif: setiap perjalanan kota mendapat 10 menit tambahan dan bandara 30 menit tambahan. Tarif dan durasi terisi April ditahan tetap. Menit tersebut menyatukan waktu antre, idle, dan perjalanan kosong."),
          table([["Rute April", "USD/jam siklus asumsi"]]+[[name(x["route"]),number(x["scenario_fare_per_hour"])] for x in m["scenarios"]["default_rows"] if x["period"]=="holdout"],[321,186]),
          p("Urutan kedua bandara berbalik karena penambahan waktu. Rumusnya: 60 x total tarif / (menit terisi + jumlah perjalanan x menit tambahan).", "small"),
          p("AMBANG IMPAS BERGANTUNG PEMBANDING", "h")]
    be=[x for x in m["scenarios"]["break_even"] if x["period"]=="holdout"]
    thresholds={(x["route"],x["city_extra_minutes"]):x["airport_extra_minutes"] for x in be}
    s += [p(f"Jika kota memiliki nol menit tambahan, ambang bandara adalah LaGuardia {number(thresholds[(routes[1],0)])} menit dan JFK {number(thresholds[(routes[0],0)])} menit. Jika kota memiliki 10 menit tambahan, ambangnya menjadi LaGuardia {number(thresholds[(routes[1],10)])} dan JFK {number(thresholds[(routes[0],10)])} menit per perjalanan."),
          p("Ambang tersebut adalah hasil aljabar skenario, bukan perkiraan antrean yang diamati atau ambang laba.","small"),PageBreak()]

    s += [p("03 / DARI TEMUAN KE PENGUJIAN", "h"),p("Ukur satu siklus.<br/>Kemudian uji keputusan.","title"),
          p("LANGKAH 1 - LENGKAPI PENGUKURAN", "h"),
          p("Catat mulai/akhir shift, waktu tersedia, antre, idle, perjalanan kosong, pickup/drop-off, seluruh tarif, dan biaya operasi. Gunakan ID pengemudi tersamarkan. Tetapkan aturan jam bertugas serta kelengkapan log sebelum melihat hasil."),
          p("LANGKAH 2 - SIAPKAN PILOT YANG SEBANDING", "h"),
          p("Acak pengemudi ke rekomendasi penempatan atau praktik biasa, dengan seluruh shift pengemudi tetap pada kelompok awal. Seimbangkan pola jam kerja dan produktivitas awal. Analisis mengikuti penugasan awal, termasuk ketika rekomendasi tidak dipatuhi."),
          p("LANGKAH 3 - TETAPKAN KEPUTUSAN SEBELUM HASIL", "h"),
          p("Metrik utama: total tarif dasar dibagi total jam bertugas. Nilai biaya per jam, jarak kosong, antrean, layanan penumpang, keselamatan, dan kelengkapan log secara terpisah. Tentukan manfaat minimum, batas kerugian, kebutuhan sampel, dan kriteria perluasan bersama pemilik operasi."),
          p("Perluas bila interval manfaat memenuhi ambang dan seluruh pembatas layanan/biaya lolos. Hentikan sesuai aturan jika terjadi kerugian atau pelanggaran. Jika interval belum memisahkan manfaat kecil dari manfaat yang layak, hasil masih belum konklusif."),
          p("BATAS BUKTI", "h"),
          p("Studi ini memakai perjalanan historis yang disaring, tanpa log shift atau biaya operasi. Interval harian tidak menghapus bias pemilihan rute. Satu bulan pembanding belum menunjukkan kestabilan semua musim. Belum ada pilot, peningkatan laba, atau penghematan yang diukur."),
          p("SUMBER DAN JEJAK PEMERIKSAAN", "h"),
          p('NYC TLC Yellow Taxi, Januari-April 2025, beserta referensi zona resmi. <link href="https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page">Halaman sumber TLC</link> dan <link href="https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf">kamus data 18 Maret 2025</link>. TLC tidak menjamin seluruh catatan. Ketentuan sumber mengikuti NYC Open Data/NYC.gov.',"small"),
          p('CSV lengkap: data/raw/ (17 bagian perjalanan dan referensi zona). Jejak sumber: data/source_manifest.json. Metodologi dan panduan data: README_ID.md serta docs/. <link href="https://nakata-airport-or-city.vercel.app/">Buka dashboard interaktif</link>.',"small")]
    doc=SimpleDocTemplate(str(OUT),pagesize=(595.2756,841.8898),rightMargin=44,leftMargin=44,topMargin=64,bottomMargin=64,title="Airport or City? - Ringkasan Eksekutif Indonesia",author="Nakata")
    doc.build(s,onFirstPage=page,onLaterPages=page)
    print(f"Ringkasan Indonesia dibuat: {OUT}")


if __name__=="__main__":
    main()
