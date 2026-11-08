"""Build the 10 Nov progress-update deck on the UW Engineering template (python-pptx).

    python3 presentation/build_update_deck_2026-11-10.py TEMPLATE.pptx OUT.pptx ASSETS_DIR

TEMPLATE.pptx is engineering_powerpoint_template_16-9_widescreen.potx with its main part's content type
switched from presentationml.template to presentationml.presentation in [Content_Types].xml (python-pptx
refuses .potx otherwise). ASSETS_DIR holds hero.png (hardware/renders/Smart_Dumbbell_Concept_Render_v02.png),
layout.png (hardware/layout/layout-v0.2.png cropped to the drawing area), rig.png (ml/figures/recording-rig-v1.png)
and schematic.png (hardware/wiring/SCH_Smart Dumbbell_2026-11-08.pdf rendered and cropped). Fonts and colours come
from the template theme (Barlow Condensed headings, Georgia body, Engineering purple accents)."""
import sys, copy
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_THEME_COLOR

TPL, OUT, ASSETS = sys.argv[1], sys.argv[2], sys.argv[3]
HERO, SCH, LAYOUT, RIG = [ASSETS + "/" + f for f in ("hero.png", "schematic.png", "layout.png", "rig.png")]

PURPLE = MSO_THEME_COLOR.ACCENT_5      # 5D0096
LILAC = MSO_THEME_COLOR.ACCENT_1       # B45DCB
MID = MSO_THEME_COLOR.ACCENT_3         # 865DA4
GRAY = MSO_THEME_COLOR.TEXT_2          # 757575
BLACK = MSO_THEME_COLOR.TEXT_1
CARD = RGBColor(0xF4, 0xF0, 0xF8)      # very light purple tint for cards
HEAD_FONT = "+mj-lt"                   # theme heading font (Barlow Condensed)

prs = Presentation(TPL)
# drop the template's sample slides
sldIdLst = prs.slides._sldIdLst
for sldId in list(sldIdLst):
    prs.part.drop_rel(sldId.rId); sldIdLst.remove(sldId)
L_TITLE_IMG, L_TITLE_ONLY = prs.slide_layouts[1], prs.slide_layouts[10]
FOOTER = "Smart Dumbbell  |  Project update  |  10 November 2026"
page_no = [0]


def set_runs(tf, items, size=14, color=BLACK, bold=False, font=None, align=None, space_after=4, line=None, bullets=False):
    """items: list of paragraphs; each a string or list of (text, {opts}) runs."""
    tf.word_wrap = True
    first = True
    for item in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph(); first = False
        if align is not None: p.alignment = align
        p.space_after = Pt(space_after)
        if line: p.line_spacing = line
        runs = item if isinstance(item, list) else [(item, {})]
        for text, o in runs:
            r = p.add_run(); r.text = text
            f = r.font; f.size = Pt(o.get("size", size)); f.bold = o.get("bold", bold)
            c = o.get("color", color)
            if isinstance(c, RGBColor): f.color.rgb = c
            else: f.color.theme_color = c
            fn = o.get("font", font)
            if fn: f.name = fn
        if bullets:
            pPr = p._p.get_or_add_pPr(); pPr.set("marL", "228600"); pPr.set("indent", "-228600")
            bu = pPr.makeelement("{http://schemas.openxmlformats.org/drawingml/2006/main}buChar", {"char": "•"})
            pPr.append(bu)


def tb(slide, x, y, w, h, items, **kw):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.margin_left = tf.margin_right = Inches(0.05); tf.margin_top = tf.margin_bottom = Inches(0.03)
    anchor = kw.pop("anchor", None)
    if anchor: tf.vertical_anchor = anchor
    set_runs(tf, items, **kw)
    return box


def card(slide, x, y, w, h, fill=CARD):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.adjustments[0] = 0.04
    s.fill.solid(); s.fill.fore_color.rgb = fill; s.line.fill.background(); s.shadow.inherit = False
    s.text_frame.text = ""
    return s


def footer(slide):
    page_no[0] += 1
    tb(slide, 0.28, 6.9, 7.0, 0.3, [FOOTER], size=10, color=GRAY)
    tb(slide, 6.11, 6.9, 1.2, 0.3, [f"PAGE {page_no[0]}"], size=10, color=GRAY)


def content_slide(title, notes):
    s = prs.slides.add_slide(L_TITLE_ONLY)
    s.shapes.title.text = title
    footer(s)
    s.notes_slide.notes_text_frame.text = notes
    return s


def table(slide, x, y, w, rows, col_w, size=12, header=True, row_h=0.32):
    shp = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(row_h * len(rows)))
    t = shp.table
    for j, cw in enumerate(col_w): t.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        t.rows[i].height = Inches(row_h)
        for j, val in enumerate(row):
            c = t.cell(i, j); c.margin_left = c.margin_right = Inches(0.06); c.margin_top = c.margin_bottom = Inches(0.03)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = c.text_frame; tf.text = ""
            p = tf.paragraphs[0]; r = p.add_run(); r.text = str(val); r.font.size = Pt(size)
            if header and i == 0:
                r.font.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF); r.font.name = HEAD_FONT; r.font.size = Pt(size + 2)
                c.fill.solid(); c.fill.fore_color.theme_color = PURPLE
            else:
                r.font.color.theme_color = BLACK
                c.fill.solid(); c.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if i % 2 else CARD
            if j > 0 and isinstance(val, str) and val and (val[0].isdigit() or val.startswith("—") or val.startswith("+")): p.alignment = PP_ALIGN.RIGHT if j == 1 else PP_ALIGN.LEFT
    # thin borders via tblPr style off: keep default
    return shp


def heading(slide, x, y, w, text, size=20, color=PURPLE):
    return tb(slide, x, y, w, 0.4, [text], size=size, bold=True, color=color, font=HEAD_FONT, space_after=0)


# ---------------- 1. cover ----------------
s = prs.slides.add_slide(L_TITLE_IMG)
s.shapes.title.text = "SMART DUMBBELL"
for ph in s.placeholders:
    idx = ph.placeholder_format.idx
    if idx == 1:
        ph.text_frame.text = "Counts bicep curls on the device, reads heart rate at the grip, logs every set to a laptop"
        for p in ph.text_frame.paragraphs:
            for r in p.runs: r.font.size = Pt(16)
    elif idx == 10:
        ph.text_frame.text = "Project update, 10 November 2026\nECE 198 Group 57: Hanson He, Eric Zhu, Zoe Wang, Julia Zhang"
    elif idx == 13:
        ph.insert_picture(HERO)
    elif idx == 11:
        ph.text_frame.text = FOOTER
tb(s, 0.5, 2.85, 6.0, 1.0, [[("Project update, 10 November 2026", {"bold": True, "color": PURPLE, "font": HEAD_FONT, "size": 16})], "ECE 198 Group 57: Hanson He, Eric Zhu, Zoe Wang, Julia Zhang"], size=12, color=GRAY, space_after=2)
s.notes_slide.notes_text_frame.text = "20 s. One sentence: a smart dumbbell for CCCARE home rehab; the dumbbell itself recognises and counts curls, reads heart rate at the grip, sends data to a laptop. Say that the picture is a concept render, not the prototype."
page_no[0] = 1

# ---------------- 2. status ----------------
s = content_slide("THREE WEEKS IN: EVERY MODULE RUNS, THE SYSTEM IS HALF INTEGRATED",
    "40 s. Three columns: works / in progress / not started, only what is on the team repository's main. Key points: four modules on one bus, the integrated firmware ran once on the board, the schematic exists, Zoe's Bluetooth dashboard is merged. Be plain: the counter and heart rate are placeholders, zero real recordings, zero acceptance tests, no printed enclosure. If the bench is wired, hold it up after this slide and press the button.")
cols = [
    ("WORKS ON THE BENCH", PURPLE, [
        "Nano ESP32 + IMU + pulse sensor + OLED on one I2C bus, 4 devices, no conflicts",
        "IMU streams 6 axes at 104 Hz, axes verified against the silkscreen",
        "Wi-Fi access point answers HTTP from a phone",
        "Integrated firmware v0: one button, display, 100 Hz pulse sampling, on-device model call",
        "Laptop logger prototype with CSV export (on a mock server)",
        "Schematic v2 drawn in EasyEDA, reviewed; Bluetooth web dashboard merged"]),
    ("IN PROGRESS THIS WEEK", LILAC, [
        "Rewiring the bench onto a half-size breadboard after the first board failed",
        "Rep counter and heart-rate detector are placeholders in the integrated app; both need real-motion tuning",
        "Recording rig and protocol ready; first 3 people this week",
        "Enclosure layout v0.2 drawn; first print this week"]),
    ("NOT STARTED", GRAY, [
        "Model trained on real recordings (pipeline tested on synthetic data only)",
        "Device-side Bluetooth service for the dashboard; logger against real firmware",
        "Any of the ten acceptance tests",
        "Printed enclosure"]),
]
for i, (h, c, items) in enumerate(cols):
    x = 0.4 + i * 4.2
    card(s, x, 1.6, 4.0, 5.1)
    heading(s, x + 0.2, 1.75, 3.6, h, 20, c)
    tb(s, x + 0.2, 2.3, 3.6, 4.3, items, size=13, bullets=True, space_after=6)
tb(s, 0.4, 6.55, 9, 0.3, ["Parts arrived 3 Nov · bring-up records in tests/results · integrated firmware first run 6 Nov"], size=10, color=GRAY)

# ---------------- 3. bench ----------------
s = content_slide("THE BENCH PROTOTYPE, MEASURED ON 3 AND 6 NOVEMBER",
    "45 s. Schematic left, serial measurements right. Stress that the numbers were read from the serial port. Tell one bug story: the display library dropped the bus to 100 kHz and a full-frame refresh delayed IMU samples; fixed by chunked transfer. End on the two rows that are not tested or not solved.")
s.shapes.add_picture(SCH, Inches(0.4), Inches(1.55), width=Inches(7.5))
rows = [["Check", "Result", "Status"], ["I2C devices found", "4 of 4", "pass"], ["IMU sample rate", "104.0 Hz", "pass"],
        ["Samples lost with display on", "0 in 20 s", "pass"], ["Pulse sampling", "100 Hz", "pass"], ["Model inference on device", "2.3 ms", "pass"],
        ["Button start / pause / end", "events logged", "pass"], ["Rep count on a real curl", "—", "not tested"], ["Heart-rate value", "9–14 bpm high", "open"]]
table(s, 8.2, 1.6, 4.7, rows, [2.4, 1.3, 1.0], size=12)
tb(s, 8.2, 4.75, 4.7, 1.6, ["Found and fixed: the display library dropped the bus to 100 kHz and a full-frame refresh delayed IMU samples; the frame is now sent in 64-byte chunks between samples."], size=12, color=GRAY)
tb(s, 0.4, 6.55, 9, 0.3, ["Schematic v2 (EasyEDA, 8 Nov) · one button on D2 · all modules on the Nano 3V3 rail · records: tests/results, 3 Nov and 6 Nov"], size=10, color=GRAY)

# ---------------- 4. motion ----------------
s = content_slide("COUNTING CURLS: A CLASSIFIER GATES A SIMPLE COUNTER",
    "45 s. Why two parts: the counter alone counts any swing, the classifier alone cannot tell one rep from two. Status: pipeline works on synthetic data only, real recordings start this week, evaluation split by person. The targets are proposed, not verified.")
steps = [("IMU 104 Hz", "3-axis accel + 3-axis gyro, X axis along the grip"),
         ("2 s window, 31 features", "mean, spread, range, zero crossings per axis; one result per second"),
         ("Classifier on the Nano", "logistic regression: curl / idle / other with confidence; trained on the laptop, exported as a C header"),
         ("Counter (placeholder)", "gyro rate crosses +60 then -60 deg/s and settles, 0.6-5 s per rep; gate on the curl label once the model is real")]
bw, gap, x0 = 2.75, 0.45, 0.4
for i, (h, d) in enumerate(steps):
    x = x0 + i * (bw + gap)
    card(s, x, 1.7, bw, 1.75, CARD if i < 3 else RGBColor(0xE6, 0xDA, 0xF2))
    heading(s, x + 0.15, 1.8, bw - 0.3, h, 17)
    tb(s, x + 0.15, 2.3, bw - 0.3, 1.1, [d], size=12)
    if i < 3:
        a = s.shapes.add_shape(MSO_SHAPE.CHEVRON, Inches(x + bw + 0.1), Inches(2.4), Inches(0.25), Inches(0.35))
        a.fill.solid(); a.fill.fore_color.theme_color = MID; a.line.fill.background()
heading(s, 0.4, 3.8, 6.0, "WHY TWO PARTS", 20)
tb(s, 0.4, 4.3, 6.0, 1.9, ["The counter alone counts any swing. The classifier alone cannot tell one rep from two. Together: a half rep, a pause or picking the dumbbell up does not count (FR-05, FR-06)."], size=15)
heading(s, 6.9, 3.8, 6.0, "WHERE IT STANDS", 20)
tb(s, 6.9, 4.3, 6.0, 2.2, ["Training pipeline and on-device inference agree to 1e-6, but only on synthetic data. The counter thresholds are guesses and have not been tested on a real curl. Real recordings start this week; evaluation is split by person, never by random windows. Target: macro-F1 ≥ 0.85, count within ±1 on 18 of 20 sets."], size=15)
tb(s, 0.4, 6.55, 9, 0.3, ["ml/workplan.md · classification: Hanson · counting and integration: Julia"], size=10, color=GRAY)

# ---------------- 5. data ----------------
s = content_slide("TRAINING DATA STARTS THIS WEEK, BEFORE THE ENCLOSURE EXISTS",
    "35 s. The question 'where does the data come from' is answered here first. Three points: the temporary rig (IMU taped to a 3 lb hex dumbbell, orientation frozen, same mounting in the enclosure), the protocol (6 people, anonymous, three curl speeds plus idle, other and half reps), and the weight evidence (senior classes 1-3 lb, cardiac rehab 1-5 lb) behind the specification: no more than 1 kg, no training ballast. Recordings at 0.9 and 1.4 kg bracket that. Zero recordings as of 8 Nov.")
s.shapes.add_picture(RIG, Inches(0.4), Inches(1.55), width=Inches(7.3))
blocks = [("RIG", "IMU taped to a 3 lb hex dumbbell, X axis along the grip, orientation photographed and frozen; the same mounting goes into the printed head."),
          ("PROTOCOL", "6 people, anonymous IDs. Per person: curls slow / normal / fast, three kinds of idle, two minutes of other movements, one minute of half reps. 104 Hz CSV over USB."),
          ("WEIGHT", "Recordings at 0.9 and 1.4 kg (2 lb and 3 lb dumbbells), bracketing the target. Specification: total mass no more than 1 kg, no added training ballast in Version 1; washers only balance the two heads. Evidence: senior strength classes use 1–3 lb, early cardiac rehab 1–5 lb.")]
for i, (h, d) in enumerate(blocks):
    y = 1.6 + i * 1.6
    heading(s, 8.0, y, 4.9, h, 18)
    tb(s, 8.0, y + 0.4, 4.9, 1.15, [d], size=12.5)
tb(s, 0.4, 6.55, 10, 0.3, ["ml/data-protocol.md · evaluation split by person, never by random windows · 0 recordings as of 8 Nov"], size=10, color=GRAY)

# ---------------- 6. heart ----------------
s = content_slide("HEART RATE AT THE GRIP IS OUR BIGGEST OPEN RISK",
    "45 s. The most candid slide. Two numbers: pulse amplitude only 0.1-0.4 % of DC, and the best estimate at rest is 9-14 bpm high. A curl at 1 Hz shares the band with heart rate, so motion makes it worse. Then hand the question to the teaching team: can the in-motion requirement be restated. This is question 1 in the Q&A.")
for i, (big, small) in enumerate([("0.1–0.4 %", "pulse amplitude relative to DC, finger still, at rest"), ("+9 to +14", "bpm error of our best offline estimate vs a watch reading 86, at rest")]):
    x = 0.4 + i * 3.7
    card(s, x, 1.6, 3.5, 1.9)
    tb(s, x + 0.2, 1.65, 3.1, 0.9, [big], size=40, bold=True, color=PURPLE if i == 0 else LILAC, font=HEAD_FONT, space_after=0)
    tb(s, x + 0.2, 2.6, 3.1, 0.85, [small], size=12, color=GRAY)
tb(s, 0.4, 3.75, 7.3, 2.7, [
    "Sensor, bus and finger detection work; the library beat detector does not. A band-pass plus peak-picking replacement is planned, not yet on the board.",
    "A curl is about 1 Hz, in the same band as heart rate, so motion will make this worse.",
    "Firmware already follows FR-08: no finger, too few beats or stale data shows HR -- and logs invalid, never an old value."], size=13, bullets=True, space_after=8)
card(s, 8.0, 1.6, 4.9, 4.85)
heading(s, 8.2, 1.75, 4.5, "NEXT TWO WEEKS", 20)
tb(s, 8.2, 2.3, 4.5, 3.2, [
    "Replace the detector with band-pass filtering and peak picking",
    "Borrow a reference device and run the 60 s synchronized comparison (AT-04)",
    "Decide before the method freeze: keep valid heart rate during motion, or report it only when signal quality allows and guarantee it between sets"], size=13, bullets=True, space_after=8)
tb(s, 8.2, 5.6, 4.5, 0.7, [[("We would like your view on that spec change today.", {"bold": True, "color": PURPLE})]], size=13)
tb(s, 0.4, 6.55, 10, 0.3, ["Measurements 3 Nov, tests/results/2026-11-03_bringup-05-max30102.md · outcome recorded as inconclusive"], size=10, color=GRAY)

# ---------------- 7. plan ----------------
s = content_slide("ENCLOSURE, THE ROAD TO 25 NOVEMBER, AND THREE QUESTIONS",
    "40 s. Layout figure, three points only: electronics and power bank in one head, washers in the other only to balance it, pulse sensor in the grip; total mass at most 1 kg per the specification. Timeline quickly; the end point is the 90-second demo on 25 Nov. Read the three questions and leave them for the Q&A.")
s.shapes.add_picture(LAYOUT, Inches(0.4), Inches(1.55), width=Inches(6.3))
tb(s, 0.4, 5.2, 6.3, 0.95, ["Layout v0.2: electronics and the 5000 mAh power bank in one hex head, steel balance washers in the other, pulse sensor flush in the grip. Total mass no more than 1 kg and no added training ballast (specification); the washer count only levels the two heads. First print this week."], size=11, color=GRAY)
rows = [["Week", "Milestone"],
        ["10–16 Nov", "Recordings from 4+ people; first real model; counter tuned offline; printed head fit check; logger talks to the real firmware"],
        ["17–21 Nov", "Model on device gating the counter; assembled dumbbell; count, interference, 10 min and reconnect tests on the device"],
        ["22–24 Nov", "Freeze, spare board flashed, three rehearsals of the 90 s demo"],
        ["25 Nov", "Symposium: start, 10 counted curls, swing not counted, grip heart rate, set logged on the laptop"]]
shp = table(s, 7.0, 1.6, 5.9, rows, [1.1, 4.8], size=11, row_h=0.5)
shp.table.rows[0].height = Inches(0.34)
card(s, 7.0, 4.55, 5.9, 1.9)
heading(s, 7.2, 4.65, 5.5, "QUESTIONS FOR YOU", 18)
tb(s, 7.2, 5.05, 5.5, 1.4, [
    "1.  May we restate the in-motion heart-rate requirement as above?",
    "2.  Symposium format: table, power, how long per visitor?",
    "3.  We are at CAD 120 of our own money; is a 200 ceiling reasonable?"], size=12.5, space_after=3)
tb(s, 0.4, 6.55, 10, 0.3, ["Enclosure: Eric · electronics and heart rate: Zoe · classification: Hanson · counting, integration, logger: Julia"], size=10, color=GRAY)

# ---------------- 8. questions ----------------
s = content_slide("QUESTIONS?",
    "Stay on this slide for the Q&A. Read the three questions first so the teaching team answers them, then take their questions. Prepared answers are in docs/update-presentation-2026-11-10.md section 3.")
card(s, 2.4, 1.9, 8.5, 2.7)
heading(s, 2.7, 2.05, 8.0, "WHAT WE WOULD LIKE YOUR VIEW ON", 22)
tb(s, 2.7, 2.7, 7.9, 2.7, [
    "1.  Heart rate during motion: keep FR-07 as written, or report it only when signal quality allows and guarantee it between sets?",
    "2.  Symposium on 25 November: table, power, time per visitor?",
    "3.  Budget: CAD 120 of our own money spent; is a 200 ceiling reasonable?"], size=16, space_after=10)
tb(s, 2.7, 4.8, 8.0, 0.5, ["Repository: github.com/juliazhang1015/smart-dumbbell"], size=13, color=GRAY)
prs.save(OUT)
print("saved", OUT, len(prs.slides), "slides")
