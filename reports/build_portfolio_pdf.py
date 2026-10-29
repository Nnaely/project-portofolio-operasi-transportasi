"""Build the standalone, submission-ready portfolio from verified saved outputs."""
from __future__ import annotations

import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/pdf/Nakata_Portofolio_Data_Analyst_Airport_or_City.pdf"
W, H = 595.2756, 841.8898
L, R = 44, 551.2756
CW = R - L
INK = colors.HexColor("#1D2925")
CREAM = colors.HexColor("#F4F0E7")
PAPER = colors.HexColor("#FCFAF4")
MUTED = colors.HexColor("#5B665F")
AMBER = colors.HexColor("#995D13")
TEAL = colors.HexColor("#376B70")
GRAY = colors.HexColor("#737A82")
LINE = colors.HexColor("#D5D6C8")
DARK = colors.HexColor("#23322C")
WEB = "https://nakata-airport-or-city.vercel.app/"
PAGE_COUNT = 8
BOXES = []


def fonts():
    for name, filename, fallback in [
        ("Body", "segoeui.ttf", "Helvetica"), ("Bold", "segoeuib.ttf", "Helvetica-Bold"),
        ("Serif", "georgia.ttf", "Times-Roman"), ("Italic", "georgiai.ttf", "Times-Italic"),
        ("Code", "consola.ttf", "Courier")]:
        path = Path("C:/Windows/Fonts") / filename
        if path.exists():
            pdfmetrics.registerFont(TTFont(name, str(path)))
        else:
            pdfmetrics.registerFont(pdfmetrics.Font(name, fallback, "WinAnsiEncoding"))
    pdfmetrics.registerFontFamily("Body", normal="Body", bold="Bold", italic="Body", boldItalic="Bold")


def n(value, digits=0):
    return f"{value:,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def route(value):
    return value.replace("→", "ke")


def para(c, text, top, x=L, width=CW, size=10.2, leading=None, font="Body", color=INK):
    style = ParagraphStyle("p", fontName=font, fontSize=size, leading=leading or size*1.45,
                           textColor=color, allowWidows=0, allowOrphans=0)
    p = Paragraph(text, style)
    _, height = p.wrap(width, H)
    if top + height > 770:
        raise ValueError(f"Text extends past content area on page {c.getPageNumber()}: {text[:60]}")
    p.drawOn(c, x, H-top-height)
    BOXES.append({"page": c.getPageNumber(), "top": top, "bottom": top+height, "text": text[:70]})
    return top+height


def label(c, text, top, x=L, color=AMBER):
    return para(c, text.upper(), top, x=x, size=8.2, leading=11, font="Bold", color=color)


def line(c, top, x=L, width=CW, color=LINE):
    c.setStrokeColor(color); c.setLineWidth(.6); c.line(x, H-top, x+width, H-top)


def rect(c, x, top, width, height, fill=PAPER):
    c.setFillColor(fill); c.rect(x, H-top-height, width, height, fill=1, stroke=0)


def frame(c, page, topic):
    rect(c, 0, 0, W, H, CREAM)
    para(c, "NAKATA / DATA ANALYST PORTFOLIO", 25, size=8, leading=10, font="Bold")
    c.setFillColor(MUTED); c.setFont("Body", 8)
    c.drawRightString(R, H-34, "AIRPORT OR CITY? / 17 OKT 2026")
    line(c, 47); line(c, 789)
    c.setFont("Italic", 9.2); c.setFillColor(AMBER)
    c.drawString(L, 35, "Documentation by Nakata")
    c.setFont("Body", 7); c.setFillColor(MUTED)
    c.drawString(L, 23, "Making this study easier to understand.")
    c.setFont("Body", 7.4)
    c.drawRightString(R, 35, f"{topic.upper()} / {page:02d} OF {PAGE_COUNT:02d}")
    c.bookmarkPage(f"page{page}")
    c.addOutlineEntry(topic, f"page{page}", level=0)


def heading(c, kicker, title, subtitle=""):
    label(c, kicker, 68)
    bottom = para(c, title, 90, size=27, leading=32, font="Serif")
    if subtitle:
        bottom = para(c, subtitle, bottom+13, size=10.2, color=MUTED)
    return bottom


def table(c, rows, top, widths, small=9):
    style=ParagraphStyle("cell",fontName="Body",fontSize=small,leading=small*1.4,textColor=INK)
    cells=[[Paragraph(str(x),style) for x in row] for row in rows]
    t=Table(cells,colWidths=widths,hAlign="LEFT")
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E5DDCD")),
        ("LINEBELOW",(0,0),(-1,0),.7,INK),("LINEBELOW",(0,1),(-1,-1),.4,LINE),
        ("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),8),
        ("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),8),
        ("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    _,height=t.wrap(CW,H)
    if top+height>770:raise ValueError(f"Table overflow on page {c.getPageNumber()}")
    t.drawOn(c,L,H-top-height)
    return top+height


def note(c, text, top):
    return para(c,text,top,size=8.4,leading=11.8,color=MUTED)


def qr(c, url, x, top, size=72):
    q=QrCodeWidget(url); bounds=q.getBounds(); scale=size/(bounds[2]-bounds[0])
    d=Drawing(size,size,transform=[scale,0,0,scale,0,0]); d.add(q)
    renderPDF.draw(d,c,x,H-top-size)
    c.linkURL(url,(x,H-top-size,x+size,H-top),relative=0)


def cover(c,m):
    frame(c,1,"Profil proyek")
    label(c,"STUDI KASUS INDEPENDEN / OPERASI TRANSPORTASI",85)
    para(c,"Airport",124,size=64,leading=70,font="Serif")
    para(c,"or City?",195,size=64,leading=74,font="Italic",color=AMBER)
    para(c,"Menilai produktivitas tarif taksi<br/>dan waktu operasi yang belum tercatat.",300,
         width=460,size=17,leading=24)
    label(c,"NAKATA / DATA ANALYST & BUSINESS ANALYST",372,color=INK)
    stats=[("15,17 juta","catatan perjalanan sumber"),("4 bulan","Januari-April 2025"),("3 rute","bandara dan dalam kota")]
    for i,(value,caption) in enumerate(stats):
        x=L+i*173
        rect(c,x,409,161,90)
        para(c,value,424,x=x+12,width=145,size=27,leading=32,font="Serif")
        para(c,caption,470,x=x+12,width=140,size=8.5,color=MUTED)
    label(c,"TEMUAN YANG MENGARAHKAN KEPUTUSAN",533)
    para(c,"LaGuardia unggul per jam terisi.<br/>Asumsi waktu kosong dapat mengubah urutannya.",554,
         size=21,leading=29,font="Serif")
    para(c,"Python / SQL / DuckDB / validasi waktu / skenario operasional",630,size=9.4,color=MUTED)
    line(c,660)
    label(c,"JELAJAHI BUKTINYA",683)
    para(c,f'<link href="{WEB}" color="#995D13">nakata-airport-or-city.vercel.app</link>',705,size=11)
    note(c,"Dashboard interaktif, memo eksekutif, dan paket analisis dapat dibuka melalui tautan atau QR.",730)
    qr(c,WEB,R-77,677,77)
    c.showPage()


def business(c,m):
    frame(c,2,"Pertanyaan bisnis")
    y=heading(c,"01 / PERTANYAAN, METRIK, KEPUTUSAN","Tarif besar belum menjawab<br/>penggunaan waktu.",
              "Pemangku kepentingan: manajer operasi armada taksi hipotetis yang mengevaluasi penempatan kendaraan.")
    y=table(c,[["Komponen","Ruang lingkup"],
       ["Keputusan","Apakah strategi menunggu penumpang di bandara layak diuji lebih lanjut?"],
       ["Pembanding","JFK ke Manhattan; LaGuardia ke Manhattan; Manhattan ke Manhattan."],
       ["Periode","Januari-Maret membentuk perbandingan awal; April memeriksa persistensi urutan."],
       ["Keluaran","Perbandingan terverifikasi, dashboard skenario, dan rencana pengukuran sebelum pilot."]],y+22,[116,CW-116])
    label(c,"METRIK UTAMA",y+24)
    rect(c,L,y+44,CW,91,DARK)
    para(c,"Tarif dasar per jam terisi",y+58,x=L+15,width=CW-30,size=14,font="Bold",color=PAPER)
    para(c,"60 x SUM(fare_amount) / SUM(duration_minutes)",y+85,x=L+15,width=CW-30,size=11,font="Code",color=PAPER)
    y=y+156
    y=para(c,"Pembilang memakai tarif dasar, tanpa tip, tol, pajak, atau biaya tambahan. Penyebut memakai waktu pickup sampai drop-off. Waktu antre, idle, dan perjalanan kosong belum tercakup.",y)
    label(c,"MENGAPA MENJUMLAHKAN DAHULU?",y+18)
    y=para(c,"Dua perjalanan masing-masing bertarif USD 20 membutuhkan 10 dan 50 menit. Totalnya USD 40 selama satu jam, sehingga hasilnya <b>USD 40/jam</b>. Rata-rata rasio per perjalanan menghasilkan USD 72/jam dan memberi bobot berlebihan pada perjalanan pendek.",y+39)
    note(c,"Definisi dibekukan sebelum pembandingan. Tarif per jam terisi mengukur produktivitas perjalanan; pendapatan bersih memerlukan seluruh waktu bertugas dan biaya operasi.",y+17)
    c.showPage()


def data_page(c,m,q,source):
    frame(c,3,"Data dan kualitas")
    y=heading(c,"02 / SUMBER DAN ALUR DATA","Jejak data yang dapat diperiksa.",
              "Sumber resmi NYC TLC Yellow Taxi dan referensi zona. Satu baris sumber mewakili satu perjalanan yang dilaporkan.")
    rows=[["Berkas sumber","Baris perjalanan"]]
    for f in source["files"]:
        if f["file"].endswith(".parquet"):rows.append([f["file"],n(f["rows"])])
    y=table(c,rows,y+19,[345,CW-345])
    label(c,"POPULASI MENYEMPIT SECARA EKSPLISIT",y+22)
    y+=47
    for text,value,color in [("Sumber",m["kpis"]["source_trips"],GRAY),("Memenuhi aturan",m["kpis"]["eligible_trips"],TEAL),("Tiga rute studi",m["kpis"]["study_trips"],AMBER)]:
        para(c,text,y,width=148,size=9)
        rect(c,L+153,y+2,value/m["kpis"]["source_trips"]*240,12,color)
        para(c,n(value),y,x=L+405,width=102,size=10,font="Bold")
        y+=29
    excluded=m["kpis"]["source_trips"]-m["kpis"]["eligible_trips"]
    outside={x["cohort_status"]:x["trips"] for x in q["waterfall"]}
    other=excluded-outside["03_outside_card_cash"]-outside["04_outside_ratecodes_1_2"]-outside["05_dst_transition_day"]
    y=table(c,[["Pengecualian pertama yang gagal","Baris"],
        ["Di luar pembayaran kartu/tunai",n(outside["03_outside_card_cash"])],
        ["Di luar kode tarif 1/2",n(outside["04_outside_ratecodes_1_2"])],
        ["Tanggal transisi DST, 9 Maret 2025",n(outside["05_dst_transition_day"])],
        ["Aturan bulan, durasi, jarak, tarif, atau zona lainnya",n(other)]],y+7,[377,CW-377],small=8.7)
    y=note(c,"Setiap baris dihitung pada aturan pertama yang gagal, sehingga pengecualian dan baris layak kembali ke total sumber. Pengecualian mempersempit studi; tidak semua baris yang dikeluarkan adalah kesalahan.",y+13)
    note(c,"SHA-256 sumber, jumlah baris, dan URL tersimpan pada manifest. Kunci zona diperiksa agar join tidak menggandakan perjalanan. CSV lokal lengkap tersedia dalam 17 bagian; analisis memakai Parquet resmi.",y+9)
    c.showPage()


def result_page(c,m,g,routes):
    frame(c,4,"Hasil dan validasi")
    y=heading(c,"03 / PERIKSA BULAN BERIKUTNYA","Urutan bertahan pada April.",
              "Tarif dasar per jam terisi, USD. Januari-Maret dan April dihitung terpisah; interval menunjukkan variasi antarhari.")
    top=y+24; x0=L+170; pw=259; plot_top=top+35
    for i,(text,color) in enumerate([("Jan-Mar",TEAL),("April",AMBER)]):
        x=L+i*116;rect(c,x,top,8,8,color);para(c,text,top-3,x=x+14,width=100,size=9,color=MUTED)
    for tick in range(0,101,20):
        x=x0+tick/100*pw
        c.setStrokeColor(LINE);c.setLineWidth(.4);c.line(x,H-plot_top,x,H-(plot_top+211))
        c.setFont("Body",8);c.setFillColor(MUTED);c.drawCentredString(x,H-(plot_top+229),str(tick))
    for i,r in enumerate(routes):
        t=plot_top+9+i*71
        para(c,route(r),t+7,width=159,size=9.5,font="Bold")
        for per,off,col in [("train",0,TEAL),("holdout",23,AMBER)]:
            x=g[(r,per)];rate=x["fare_per_occupied_hour"]
            rect(c,x0,t+off,rate/100*pw,13,col)
            yl=H-t-off-6.5
            lo=x0+x["ci_low"]/100*pw;hi=x0+x["ci_high"]/100*pw
            c.setStrokeColor(INK);c.setLineWidth(.8);c.line(lo,yl,hi,yl);c.line(lo,yl-3,lo,yl+3);c.line(hi,yl-3,hi,yl+3)
            para(c,n(rate,2),t+off-1,x=R-51,width=51,size=9,font="Bold")
    y=plot_top+250
    y=note(c,"Interval persentil 95% dari 2.000 bootstrap hari kalender berpasangan. Seluruh rute menggunakan pilihan hari yang sama. Ketergantungan antarhari dan perbedaan pengemudi yang tidak terukur tetap menjadi batas analisis.",y)
    rows=[["April","Perjalanan","Tarif/trip (USD)","Menit/trip","USD/jam terisi"]]
    for r in routes:
        x=g[(r,"holdout")];rows.append([route(r),n(x["trips"]),n(x["mean_fare_usd"],2),n(x["mean_minutes"],2),n(x["fare_per_occupied_hour"],2)])
    y=table(c,rows,y+20,[156,84,91,76,CW-407],small=8.5)
    city=g[(routes[2],"holdout")]["fare_per_occupied_hour"]
    lift=(g[(routes[1],"holdout")]["fare_per_occupied_hour"]/city-1)*100
    y=para(c,f"<b>Interpretasi:</b> LaGuardia berada {n(lift,1)}% di atas kota pada metrik waktu terisi. JFK memiliki tarif per perjalanan lebih besar, tetapi durasinya lebih panjang. Perbandingan historis ini belum mengukur dampak mengirim lebih banyak taksi ke bandara.",y+20)
    c.showPage()


def scenario_page(c,m,g,routes):
    frame(c,5,"Skenario waktu")
    y=heading(c,"04 / NYATAKAN ASUMSI YANG HILANG","Waktu kosong dapat<br/>membalik urutan bandara.",
              "Skenario April: waktu tambahan kota ditahan 10 menit per perjalanan; ubah asumsi waktu tambahan bandara dari 0 sampai 120 menit.")
    x0=L+41;pw=CW-64;top=y+32;ph=184;bottom=top+ph
    def py(rate):return H-bottom+rate/100*ph
    for tick in range(0,101,20):
        yy=py(tick);c.setStrokeColor(LINE);c.setLineWidth(.5);c.line(x0,yy,x0+pw,yy)
        c.setFont("Body",8);c.setFillColor(MUTED);c.drawRightString(x0-9,yy-3,str(tick))
    for tick in [0,30,60,90,120]:
        xx=x0+tick/120*pw;c.setFont("Body",8);c.setFillColor(MUTED);c.drawCentredString(xx,H-bottom-16,str(tick))
    city=g[(routes[2],"holdout")];city_rate=60*city["fare_usd"]/(city["occupied_minutes"]+city["trips"]*10)
    c.setStrokeColor(GRAY);c.setLineWidth(1);c.setDash(4,3);c.line(x0,py(city_rate),x0+pw,py(city_rate));c.setDash()
    for r,col in [(routes[0],AMBER),(routes[1],TEAL)]:
        x=g[(r,"holdout")];path=c.beginPath()
        for wait in range(121):
            rate=60*x["fare_usd"]/(x["occupied_minutes"]+x["trips"]*wait)
            xx=x0+wait/120*pw;yy=py(rate)
            path.moveTo(xx,yy) if wait==0 else path.lineTo(xx,yy)
        c.setStrokeColor(col);c.setLineWidth(2);c.drawPath(path)
    para(c,"USD / jam siklus asumsi",top-19,x=x0,width=220,size=8,color=MUTED)
    para(c,"Menit tambahan bandara per perjalanan",bottom+24,x=x0,width=pw,size=8,color=MUTED)
    legends=[("JFK",AMBER),("LaGuardia",TEAL),("Kota +10 menit",GRAY)]
    for i,(text,col) in enumerate(legends):
        xx=L+i*160;rect(c,xx,bottom+50,18,3,col);para(c,text,bottom+44,x=xx+25,width=130,size=8.8,color=MUTED)
    y=bottom+81
    defaults={x["route"]:x for x in m["scenarios"]["default_rows"] if x["period"]=="holdout"}
    rows=[["Asumsi tambahan","Rute","USD/jam siklus"]]
    for r in [routes[0],routes[1],routes[2]]:
        rows.append([f"{defaults[r]['assumed_extra_minutes']} menit",route(r),n(defaults[r]["scenario_fare_per_hour"],2)])
    y=table(c,rows,y,[127,247,CW-374],small=8.8)
    be={(x["route"],x["city_extra_minutes"]):x["airport_extra_minutes"] for x in m["scenarios"]["break_even"] if x["period"]=="holdout"}
    y=para(c,f"Dengan kota +10 menit, ambang tambahan bandara yang menyamai kota adalah <b>{n(be[(routes[1],10)],2)} menit untuk LaGuardia</b> dan <b>{n(be[(routes[0],10)],2)} menit untuk JFK</b> per perjalanan.",y+17)
    note(c,"Menit tambahan adalah asumsi; bukan antrean yang diobservasi. Skenario menahan komposisi tarif dan durasi tetap serta belum memasukkan biaya. Filter sensitivitas yang lebih longgar mempertahankan urutan produktivitas terisi.",y+11)
    c.showPage()


def technical(c,m):
    frame(c,6,"Implementasi")
    y=heading(c,"05 / IMPLEMENTASI YANG BISA DITELUSURI","Dari sumber ke keputusan.",
              "Python mengatur proses; DuckDB menjalankan SQL; agregat yang sama dipakai oleh notebook, dashboard, dan dokumen keputusan.")
    y+=24
    for i,(title,body) in enumerate([("01 / Sumber","Parquet + zona\nmanifest SHA-256"),("02 / Mart SQL","join + kelayakan\nperiode + rute"),("03 / Agregat","tarif + durasi\nbootstrap + skenario"),("04 / Output","notebook + PDF\ndashboard interaktif")]):
        xx=L+i*130
        rect(c,xx,y,117,87)
        para(c,title,y+13,x=xx+10,width=100,size=8.4,font="Bold",color=AMBER)
        para(c,body.replace('\n','<br/>'),y+37,x=xx+10,width=99,size=8.1,leading=12,color=MUTED)
    label(c,"QUERY INTI / sql/02_business_questions.sql",y+111)
    sql="""SELECT period, route,
       COUNT(*) AS trips,
       SUM(fare_amount) AS fare_usd,
       SUM(duration_minutes) AS occupied_minutes,
       60 * SUM(fare_amount) / SUM(duration_minutes)
           AS fare_per_occupied_hour
FROM comparison_trips
GROUP BY period, route
ORDER BY period, fare_per_occupied_hour DESC;"""
    code_top=y+137
    rect(c,L,code_top,CW,145,DARK)
    c.setFillColor(PAPER);c.setFont("Code",9)
    for i,row in enumerate(sql.splitlines()):c.drawString(L+14,H-code_top-20-i*13,row)
    y=code_top+166
    rows=[["Bukti implementasi","Yang diperiksa"],
      ["9 pemeriksaan kualitas","Jumlah sumber, kunci zona unik, rekonsiliasi pengecualian, rute/hari, dan kohort sensitivitas."],
      ["11 uji analitis","Rasio jumlah, skenario, batas bulan, DST, join, retensi tanda tangan berulang, dan lingkup tarif/pembayaran."],
      ["Notebook dengan keluaran","Enam sel kode dijalankan dan keluarannya disimpan; angka utama ditautkan ke agregat proyek."]]
    y=table(c,rows,y,[146,CW-146],small=8.8)
    note(c,"Jejak verifikasi awal: 14 Oktober 2026; notebook Indonesia dan CSV: 15 Oktober 2026. Angka dan status diambil dari keluaran tersimpan. Tidak ada deduplikasi tanpa ID perjalanan yang stabil.",y+14)
    c.showPage()


def decision(c,m):
    frame(c,7,"Rekomendasi")
    y=heading(c,"06 / REKOMENDASI DAN BATAS BUKTI","Ukur siklus penuh.<br/>Lalu uji prioritas operasi.",
              "Usulan untuk pemilik operasi: pengukuran bertahap, metrik yang dibekukan, dan keputusan perluasan yang ditentukan sebelum hasil dilihat.")
    steps=[("01","Lengkapi waktu dan biaya","Catat mulai/akhir shift, antre, idle, perjalanan kosong, pickup/drop-off, tarif, dan biaya. Definisikan jam bertugas serta aturan log yang hilang."),
           ("02","Bandingkan kelompok yang sepadan","Acak pada tingkat pengemudi; seluruh shift tetap mengikuti kelompok awal. Seimbangkan pola jam kerja dan produktivitas baseline. Analisis mengikuti penugasan awal."),
           ("03","Tetapkan ukuran keberhasilan","Utama: total tarif dasar / total jam bertugas. Tentukan manfaat minimum, kebutuhan sampel, biaya, kualitas layanan, keselamatan, dan aturan penghentian.")]
    y+=22
    for num,title,body in steps:
        para(c,num,y,width=36,size=23,font="Italic",color=AMBER)
        para(c,title,y+1,x=L+48,width=CW-48,size=11,font="Bold")
        end=para(c,body,y+25,x=L+48,width=CW-48,size=9.6)
        y=end+22
    label(c,"GERBANG KEPUTUSAN",y)
    y=table(c,[["Perluas","Jangan perluas / hentikan","Belum konklusif"],
       ["Manfaat memenuhi ambang yang disepakati dan pembatas biaya/layanan lolos.","Kerugian atau pelanggaran batas keselamatan/layanan memenuhi aturan penghentian.","Interval masih mencakup manfaat yang terlalu kecil dan manfaat yang layak."]],y+23,[169,169,CW-338],small=8.6)
    label(c,"BATAS YANG MENENTUKAN CARA MEMAKAI HASIL",y+20)
    y=para(c,"Data tidak mengukur waktu antre dan shift lengkap, biaya pengemudi, atau efek kausal penempatan. Pemilihan rute dan ketergantungan antarhari tetap mungkin. Satu bulan validasi belum mewakili semua musim atau operasi transportasi Indonesia.",y+42,size=9.6)
    note(c,"Status: rancangan pengukuran dan pilot. Belum ada implementasi operasional, peningkatan laba, atau penghematan yang diukur dalam proyek ini.",y+12)
    c.showPage()


def evidence(c,m):
    frame(c,8,"Bukti dan sumber")
    y=heading(c,"07 / TELUSURI PROYEK","Buka analisisnya.<br/>Periksa keputusan di baliknya.",
              "Karya portofolio independen berbasis data publik. Tautan berikut aktif di dalam PDF agar pembaca dapat menelusuri hasil dan sumber.")
    items=[("Dashboard interaktif",WEB,"Pilih periode, ubah asumsi waktu, dan periksa pola jam pickup."),
      ("Memo eksekutif",WEB+"downloads/EXECUTIVE_MEMO.pdf","Ringkasan keputusan dan bukti dalam bahasa Inggris."),
      ("Paket analisis",WEB+"downloads/analysis-project.zip","SQL, Python, notebook, metode, metadata sumber, dan hasil agregat. Data mentah diunduh terpisah.")]
    y+=23
    for title,url,body in items:
        para(c,f'<link href="{url}" color="#995D13"><b>{title} / buka tautan</b></link>',y,size=11)
        y=para(c,body,y+23,size=9.5,color=MUTED)+19
    label(c,"KOMPETENSI YANG DITUNJUKKAN",y)
    y=table(c,[["Kompetensi","Bukti dalam studi"],
      ["Analisis bisnis","Satu pertanyaan keputusan, metrik dan penyebut yang eksplisit, serta rancangan pilot."],
      ["SQL dan pemodelan data","Join zona dua peran, aturan kelayakan, agregasi, dan pemisahan periode."],
      ["Penalaran statistik","Rasio jumlah, bootstrap harian berpasangan, validasi waktu, dan sensitivitas."],
      ["Komunikasi analisis","Visual, asumsi yang dapat diubah, dokumentasi, dan batas interpretasi."]],y+22,[150,CW-150],small=8.7)
    label(c,"SUMBER PRIMER",y+20)
    sources=[("NYC TLC / Yellow Taxi Trip Records",m["source"]["url"]),
      ("Yellow Taxi Data Dictionary / 18 Maret 2025",m["source"]["dictionary"]),
      ("Ketentuan NYC Open Data","https://data.cityofnewyork.us/stories/s/Terms-of-Use/k9k7-3cje/")]
    y+=43
    for title,url in sources:
        y=para(c,f'<link href="{url}" color="#995D13">{escape(title)}</link>',y,size=8.6)+8
    note(c,"Sumber periode Januari-April 2025; unduhan dipatok dengan SHA-256 pada manifest proyek. NYC TLC tidak menjamin seluruh catatan. Tidak ada afiliasi atau dukungan resmi NYC TLC yang dinyatakan. Lisensi kode proyek dan ketentuan data sumber dijelaskan dalam paket analisis.",y+5)
    c.showPage()


def main():
    fonts()
    m=json.loads((ROOT/"outputs/metrics.json").read_text(encoding="utf-8"))
    q=json.loads((ROOT/"outputs/quality_report.json").read_text(encoding="utf-8"))
    src=json.loads((ROOT/"data/source_manifest.json").read_text(encoding="utf-8"))
    assert q["all_checks_passed"] and sum(x["trips"] for x in q["waterfall"])==m["kpis"]["source_trips"]
    g={(x["route"],x["period"]):x for x in m["groups"]}
    routes=sorted({x["route"] for x in m["groups"]},key=lambda x:0 if x.startswith("JFK") else 1 if x.startswith("LaGuardia") else 2)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
    c.setTitle("Nakata | Portofolio Data Analyst - Airport or City?")
    c.setAuthor("Nakata")
    c.setSubject("Studi kasus NYC TLC: data, metode, produktivitas tarif, skenario waktu, dan rencana pilot")
    cover(c,m);business(c,m);data_page(c,m,q,src);result_page(c,m,g,routes)
    scenario_page(c,m,g,routes);technical(c,m);decision(c,m);evidence(c,m)
    c.save()
    preview=ROOT/"tmp/pdfs/portfolio";preview.mkdir(parents=True,exist_ok=True)
    (preview/"layout_boxes.json").write_text(json.dumps(BOXES,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"pdf":str(OUT),"bytes":OUT.stat().st_size,"pages":PAGE_COUNT}))


if __name__=="__main__":main()
