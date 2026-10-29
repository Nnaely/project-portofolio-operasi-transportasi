"""Create the executive decision memo from the reproducible analysis outputs.

The PDF embeds vector charts. Business metrics are always read from metrics.json.
Run this script only after the analysis pipeline has finished.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "EXECUTIVE_MEMO.pdf"
PAGE_W, PAGE_H = 595.2756, 841.8898
MARGIN = 44
WIDTH = PAGE_W - MARGIN * 2
CREAM = colors.HexColor("#F4F0E7")
PAPER = colors.HexColor("#FCFAF4")
INK = colors.HexColor("#1D2925")
MUTED = colors.HexColor("#5E6860")
LINE = colors.HexColor("#D5D6C8")
AMBER = colors.HexColor("#AD692D")
MOSS = colors.HexColor("#596D50")
SAND = colors.HexColor("#E5DDCD")


def setup_fonts():
    fonts = {
        "Body": ("segoeui.ttf", "Helvetica"),
        "Bold": ("segoeuib.ttf", "Helvetica-Bold"),
        "Serif": ("georgia.ttf", "Times-Roman"),
        "SerifBold": ("georgiab.ttf", "Times-Bold"),
        "SerifItalic": ("georgiai.ttf", "Times-Italic"),
    }
    for alias, (filename, fallback) in fonts.items():
        path = Path("C:/Windows/Fonts") / filename
        if path.exists():
            pdfmetrics.registerFont(TTFont(alias, str(path)))
        else:
            pdfmetrics.registerFont(pdfmetrics.Font(alias, fallback, "WinAnsiEncoding"))
    pdfmetrics.registerFontFamily("Body", normal="Body", bold="Bold", italic="Body", boldItalic="Bold")


def p(c, text, x, top, width, size=10, leading=None, color=INK, font="Body"):
    """Top coordinates are points from the top edge. Return rendered height."""
    style = ParagraphStyle(
        "memo", fontName=font, fontSize=size, leading=leading or size * 1.42,
        textColor=color, alignment=TA_LEFT, spaceAfter=0, allowWidows=0, allowOrphans=0,
    )
    para = Paragraph(text, style)
    _, height = para.wrap(width, PAGE_H)
    para.drawOn(c, x, PAGE_H - top - height)
    return height


def label(c, text, x, top, color=MUTED, size=8.2):
    c.setFont("Bold", size)
    c.setFillColor(color)
    c.drawString(x, PAGE_H - top - size, text.upper())


def rule(c, top, x=MARGIN, width=WIDTH, color=LINE):
    c.setStrokeColor(color)
    c.setLineWidth(0.7)
    c.line(x, PAGE_H - top, x + width, PAGE_H - top)


def box(c, x, top, width, height, fill=PAPER):
    c.setFillColor(fill)
    c.rect(x, PAGE_H - top - height, width, height, fill=1, stroke=0)


def base(c, page, topic):
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    label(c, "NYC / TAXI SHIFT ECONOMICS", MARGIN, 28, INK, 8)
    c.setFont("Body", 8)
    c.setFillColor(MUTED)
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 36, "DECISION MEMO  /  14 OCT 2026")
    rule(c, 48)
    rule(c, 790)
    c.setFillColor(AMBER)
    c.setFont("SerifItalic", 9.3)
    c.drawString(MARGIN, 35, "Documentation by Nakata")
    c.setFillColor(MUTED)
    c.setFont("Body", 7)
    c.drawString(MARGIN, 23, "Making this study easier to understand.")
    c.setFont("Body", 7.3)
    c.drawRightString(PAGE_W - MARGIN, 35, f"{topic.upper()}  /  0{page}")


def headline(c, kicker, title, subtitle=None):
    label(c, kicker, MARGIN, 68, AMBER)
    height = p(c, title, MARGIN, 91, WIDTH, 29, 33.5, INK, "Serif")
    if subtitle:
        p(c, subtitle, MARGIN, 101 + height, WIDTH, 10.4, 15, MUTED)


def fmt_n(value):
    return f"{int(value):,}"


def fmt_pct(value):
    return f"{value * 100:.1f}%"


def money(value, digits=1):
    return f"${value:,.{digits}f}"


def route_label(route):
    if route.startswith("JFK"):
        return "JFK to Manhattan"
    if route.startswith("LaGuardia"):
        return "LaGuardia to Manhattan"
    return "Manhattan to Manhattan"


def compact(value):
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}m"
    return fmt_n(value)


def number(c, text, x, top, size=27, color=INK):
    return p(c, escape(str(text)), x, top, 180, size, size * 1.12, color, "Serif")


def source_note(c, text, top=754):
    return p(c, text, MARGIN, top, WIDTH, 7.4, 10.2, MUTED)


def page_one(c, metrics, groups, routes):
    base(c, 1, "Decision")
    headline(c, "01 / A BUSINESS QUESTION WITH A MEASUREMENT BOUNDARY",
             "Price the trip.<br/>Then price the missing time.",
             "Should a yellow-taxi operator favor airport-to-Manhattan trips over trips within Manhattan?")
    selected = sum(g["trips"] for g in metrics["groups"])
    city = next(r for r in routes if r.startswith("Manhattan"))
    winner = max(routes, key=lambda r: groups[(r, "holdout")]["fare_per_occupied_hour"])
    win = groups[(winner, "holdout")]
    gaps = {x["route"]: x["airport_extra_minutes"] for x in metrics["scenarios"]["break_even"] if x["period"] == "holdout" and x["city_extra_minutes"] == 0}
    threshold = gaps.get(winner)
    rule(c, 222)
    xs = [MARGIN, MARGIN + 175, MARGIN + 348]
    values = [compact(selected), money(win["fare_per_occupied_hour"]) + "/h", f"{threshold:.1f} min" if threshold is not None else "Unmeasured"]
    captions = ["selected-route trips\nJanuary-April 2025", f"April leader\n{route_label(winner)}", "extra time to parity*\nApril scenario"]
    for x, val, caption in zip(xs, values, captions):
        number(c, val, x, 242, 26)
        p(c, caption.replace("\n", "<br/>"), x, 281, 156, 9.3, 13.1, MUTED)
    rule(c, 327)

    label(c, "RECOMMENDED DECISION", MARGIN, 348, AMBER)
    p(c, "Fund a small time-measurement pilot before changing dispatch priorities.",
      MARGIN, 369, WIDTH, 19.5, 25, INK, "Serif")
    ratio = win["fare_per_occupied_hour"] / groups[(city, "holdout")]["fare_per_occupied_hour"]
    p(c, f"The April occupied-time comparison favors <b>{escape(route_label(winner))}</b>: "
      f"{money(win['fare_per_occupied_hour'])} per occupied hour versus "
      f"{money(groups[(city, 'holdout')]['fare_per_occupied_hour'])} for Manhattan trips "
      f"({ratio:.2f}x). That comparison omits the time needed to obtain the trip and return to service.",
      MARGIN, 432, WIDTH, 10.8, 15.7)

    box(c, MARGIN, 511, WIDTH, 107, INK)
    label(c, "METRIC CONTRACT", MARGIN + 17, 528, SAND)
    p(c, "Fare per occupied hour = total fare_amount / total occupied minutes x 60",
      MARGIN + 17, 550, WIDTH - 34, 12, 17, PAPER, "Bold")
    p(c, "A duration-weighted ratio of sums. Fare excludes tips, tolls and separate surcharges. "
      "It is a trip productivity measure; full-shift income and profit require additional time and cost data.",
      MARGIN + 17, 579, WIDTH - 34, 9, 12.2, PAPER)

    label(c, "POPULATION & ELIGIBILITY", MARGIN, 642)
    p(c, f"{fmt_n(selected)} study trips / {fmt_n(metrics['kpis']['source_trips'])} source records. "
      "Pickups: 01 Jan-30 Apr 2025. Jan-Mar calibrates; April checks. "
      "Eligibility: card/cash; rate codes 1/2; duration 1-180 minutes; distance above 0 and at most 100 miles; "
      "base fare above $0 and at most $500; known zones; pickup month matches file. "
      "Trips touching 09 Mar 2025 are excluded for clock-change ambiguity.",
      MARGIN, 663, WIDTH, 9.2, 13.2, MUTED)
    source_note(c, "*Parity assumes zero unobserved time for the Manhattan benchmark; airport extra minutes are assumed, not recorded. "
                "Source: NYC TLC, Yellow Taxi Trip Records, Jan-Apr 2025. Source links and limits on page 3.", 745)
    c.showPage()


def page_two(c, metrics, groups, routes):
    base(c, 2, "Evidence")
    headline(c, "02 / HOLD THE QUESTION FIXED, CHECK A LATER MONTH",
             "Does the route ranking<br/>survive April?",
             "The comparison uses base fare divided by occupied time. Error bars resample whole calendar days.")
    x0, plot_w = 218, 265
    xmax = math.ceil(max(groups[(r, t)]["ci_high"] for r in routes for t in ("train", "holdout")) / 20) * 20
    label(c, "FARE PER OCCUPIED HOUR / USD", MARGIN, 221, INK)
    for x, text, fill in [(MARGIN, "Jan-Mar calibration", MOSS), (MARGIN + 182, "April holdout", AMBER)]:
        box(c, x, 244, 8, 8, fill)
        p(c, text, x + 14, 239, 155, 8.7, 12, MUTED)
    for tick in range(0, int(xmax) + 1, 20):
        xx = x0 + tick / xmax * plot_w
        c.setStrokeColor(LINE)
        c.setLineWidth(0.45)
        c.line(xx, PAGE_H - 270, xx, PAGE_H - 490)
        c.setFillColor(MUTED)
        c.setFont("Body", 7.5)
        c.drawCentredString(xx, PAGE_H - 509, f"${tick}")
    for i, route in enumerate(routes):
        y = 278 + i * 78
        p(c, route_label(route), MARGIN, y + 4, 160, 11.3, 15, INK, "Bold")
        for period, offset, color in [("train", 0, MOSS), ("holdout", 25, AMBER)]:
            g = groups[(route, period)]
            yy = y + offset
            rate = g["fare_per_occupied_hour"]
            box(c, x0, yy, rate / xmax * plot_w, 13, color)
            xl = x0 + g["ci_low"] / xmax * plot_w
            xh = x0 + g["ci_high"] / xmax * plot_w
            ypdf = PAGE_H - yy - 6.5
            c.setStrokeColor(INK)
            c.setLineWidth(1)
            c.line(xl, ypdf, xh, ypdf)
            c.line(xl, ypdf - 3, xl, ypdf + 3)
            c.line(xh, ypdf - 3, xh, ypdf + 3)
            c.setFillColor(INK)
            c.setFont("Bold", 10)
            c.drawRightString(PAGE_W - MARGIN, PAGE_H - yy - 10, money(rate))
    label(c, "DENOMINATORS / TRIPS AND OCCUPIED HOURS", MARGIN, 534, INK)
    rule(c, 555)
    label(c, "ROUTE", MARGIN, 566, size=7.6)
    label(c, "JAN-MAR", MARGIN + 190, 566, size=7.6)
    label(c, "APRIL", MARGIN + 355, 566, size=7.6)
    for i, route in enumerate(routes):
        y = 588 + i * 32
        p(c, route_label(route), MARGIN, y, 180, 9.1, 12)
        for period, xx in [("train", MARGIN + 190), ("holdout", MARGIN + 355)]:
            g = groups[(route, period)]
            p(c, f"{fmt_n(g['trips'])} trips<br/>{fmt_n(g['occupied_minutes'] / 60)} occupied hours", xx, y, 145, 8.6, 11.1, MUTED)
    rule(c, 686)
    preserved = metrics["holdout"]["ranking_preserved"]
    p(c, ("<b>The complete route ranking is preserved in April.</b> " if preserved else "<b>The complete route ranking changes in April.</b> ") +
      "This is a descriptive temporal check. Trip mix, hour of day and congestion can still explain differences between routes.",
      MARGIN, 704, WIDTH, 10, 14)
    source_note(c, "95% percentile intervals: 2,000 calendar-day bootstrap replicates, separately by period. "
                "Intervals describe day-to-day variation under the resampling assumption; they do not establish a dispatch-policy effect.", 752)
    c.showPage()


def page_three(c, metrics, groups, routes):
    base(c, 3, "Action")
    headline(c, "03 / TURN AN UNOBSERVED INPUT INTO A TESTABLE DECISION",
             "How much missing time<br/>erases the premium?",
             "A sensitivity calculation exposes the operating condition that the trip records cannot measure.")
    city = next(r for r in routes if r.startswith("Manhattan"))
    city_rate = groups[(city, "holdout")]["fare_per_occupied_hour"]
    thresholds = {x["route"]: x["airport_extra_minutes"] for x in metrics["scenarios"]["break_even"] if x["period"] == "holdout" and x["city_extra_minutes"] == 0}
    thresholds_ten = {x["route"]: x["airport_extra_minutes"] for x in metrics["scenarios"]["break_even"] if x["period"] == "holdout" and x["city_extra_minutes"] == 10}
    airports = [r for r in routes if r != city]
    for i, route in enumerate(airports):
        xx = MARGIN + i * (WIDTH / 2 + 7)
        ww = WIDTH / 2 - 7
        box(c, xx, 222, ww, 111, PAPER)
        label(c, route_label(route), xx + 14, 237, AMBER, 7.8)
        number(c, f"{thresholds[route]:.1f} min", xx + 14, 259, 29, AMBER)
        p(c, "city added time = 0 min per trip<br/>" + f"If city adds 10 min: <b>{thresholds_ten[route]:.1f} min</b>", xx + 14, 299, ww - 28, 8.3, 11.3, MUTED)
    p(c, f"Scenario: hold April fare and occupied time fixed; add the same unobserved minutes to every airport trip. "
      f"The Manhattan comparator remains {money(city_rate)}/h with <b>zero</b> added time. "
      "These break-even values are sensitivity thresholds, not estimates of real queues or a prediction of earnings.",
      MARGIN, 351, WIDTH, 10, 14.5)
    rule(c, 425)
    label(c, "PROPOSED PILOT / OPERATIONS + ANALYTICS", MARGIN, 445, INK)
    steps = [
        ("01", "Measure the whole cycle", "Capture queue, repositioning, idle and occupied minutes alongside fare and actual operating costs. Define the start and end of each duty block."),
        ("02", "Compare like operating windows", "Randomize feasible dispatch strategies within comparable time blocks, with driver participation. Record weather, day and congestion; set a sample-size plan after baseline measurement."),
        ("03", "Use an explicit decision gate", "Primary: base fare per full duty-hour. Separately assess cost-adjusted contribution and service quality. Adopt a policy only after the measured benefit clears a pre-agreed threshold."),
    ]
    yy = 470
    for num, title, body in steps:
        number(c, num, MARGIN, yy - 1, 19, AMBER)
        p(c, title, MARGIN + 42, yy, WIDTH - 42, 10.4, 14, INK, "Bold")
        hh = p(c, body, MARGIN + 42, yy + 20, WIDTH - 42, 9.2, 12.8, MUTED)
        yy += 26 + hh + 13
    rule(c, 702)
    p(c, "<b>Evidence boundary.</b> Historical filtered trips are not a random policy experiment. "
      "Public records lack a linked full-shift activity log, queue time and operating expenses. "
      "Day-level intervals cannot remove selection bias. TLC does not warrant record accuracy.",
      MARGIN, 715, WIDTH, 8.1, 11.1, MUTED)
    p(c, 'Source: <link href="https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page" color="#5E6860">nyc.gov/site/tlc/about/tlc-trip-record-data.page</link><br/>'
      '<link href="https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf" color="#5E6860">Yellow Taxi Data Dictionary (18 Mar 2025)</link> | '
      '<link href="https://www.nyc.gov/home/terms-of-use.page" color="#5E6860">NYC terms of use</link> | '
      'Jan-Apr 2025 Parquet files; source hashes recorded in the project manifest.',
      MARGIN, 759, WIDTH, 7.2, 9.8, MUTED)
    c.showPage()


def main():
    setup_fonts()
    metrics = json.loads((ROOT / "outputs" / "metrics.json").read_text(encoding="utf-8"))
    create_report(metrics)


def create_report(metrics):
    groups = {(g["route"], g["period"]): g for g in metrics["groups"]}
    routes = sorted({g["route"] for g in metrics["groups"]}, key=lambda r: (0 if r.startswith("JFK") else 1 if r.startswith("LaGuardia") else 2))
    assert len(routes) == 3 and all((r, t) in groups for r in routes for t in ("train", "holdout"))
    assert all(g["trips"] > 0 and g["occupied_minutes"] > 0 for g in groups.values())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle("Taxi Shift Economics - Executive Decision Memo")
    c.setAuthor("Nakata")
    c.setSubject("NYC yellow-taxi route productivity, April holdout and missing-time sensitivity")
    page_one(c, metrics, groups, routes)
    page_two(c, metrics, groups, routes)
    page_three(c, metrics, groups, routes)
    c.save()
    print(f"Created {OUT}")


if __name__ == "__main__":
    main()
