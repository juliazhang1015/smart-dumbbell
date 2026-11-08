# Recording rig for IMU training data before the enclosure exists. Run: python3 ml/figures/gen_recording_rig.py ml/figures/recording-rig-v1.svg
import sys, math, os, re
WITH_B = os.environ.get("RIG_B", "0") == "1"      # RIG_B=1 also draws the rod-and-bottles fallback
def tr(s): return s
W, H = 1500, (1000 if WITH_B else 640)
F = "PingFang SC, Helvetica Neue, Arial, sans-serif"
o = []
def a(s): o.append(s)
def text(x, y, s, size=14, anchor="start", weight="normal", fill="#222"):
    s = tr(s)
    a(f"<text x='{x}' y='{y}' font-size='{size}' text-anchor='{anchor}' font-weight='{weight}' fill='{fill}' font-family='{F}'>{s}</text>")
def rect(x, y, w, h, fill, stroke="#222", sw=1.5, rx=6, dash=None):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    a(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{rx}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}'{d}/>")
def line(x1, y1, x2, y2, stroke="#222", w=1.5, dash=None):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    a(f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{stroke}' stroke-width='{w}' stroke-linecap='round'{d}/>")
def arrow(x1, y1, x2, y2, c, label):
    line(x1, y1, x2, y2, c, 3)
    ang = math.atan2(y2 - y1, x2 - x1)
    p = [(x2, y2), (x2 - 14 * math.cos(ang - 0.4), y2 - 14 * math.sin(ang - 0.4)), (x2 - 14 * math.cos(ang + 0.4), y2 - 14 * math.sin(ang + 0.4))]
    a(f"<polygon points='{' '.join(f'{x},{y}' for x, y in p)}' fill='{c}'/>")
    if x2 < x1: text(x2 - 8, y2 + 5, label, 15, "end", "bold", c)
    elif y2 < y1: text(x2, y2 - 8, label, 15, "middle", "bold", c)
    else: text(x2 + 8, y2 + 5, label, 15, "start", "bold", c)
def hexside(cx, cy, w, h, fill):   # hex prism seen from the side: rectangle with the two flat-edge lines
    rect(cx - w / 2, cy - h / 2, w, h, fill, "#222", 2, 4)
    line(cx - w / 2, cy - h / 4, cx + w / 2, cy - h / 4, "#555", 1); line(cx - w / 2, cy + h / 4, cx + w / 2, cy + h / 4, "#555", 1)
def label(px, py, tx, ty, s, anchor="start"):
    line(px, py, tx, ty, "#777", 1); a(f"<circle cx='{px}' cy='{py}' r='3' fill='#777'/>"); text(tx + (4 if anchor == "start" else -4), ty + 5, s, 13.5, anchor, fill="#333")

a(f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><rect width='{W}' height='{H}' fill='white'/>")
text(30, 40, "Temporary rig for recording IMU training data, v1 (until the enclosure exists)", 24, weight="bold")
text(30, 66, "Only the Nano and the 4517 move with the dumbbell; one USB-C cable goes to the laptop. 4517 orientation, fixed once chosen: X along the grip toward the grip, component side up when the dumbbell rests flat.", 14, fill="#444")

# ---------- Panel A: 2 lb hex neoprene dumbbell ----------
text(30, 110, "2-3 lb neoprene hex dumbbell (GoZone, CAD 4-15)" if WITH_B else "2-3 lb neoprene hex dumbbell (GoZone, CAD 4-15)", 17, weight="bold", fill="#1a4d8f")
cy = 300
hexside(230, cy, 150, 150, "#7a7f88"); hexside(770, cy, 150, 150, "#7a7f88")
rect(305, cy - 18, 390, 36, "#9aa0a8", "#222", 2, 18)     # handle
text(500, cy + 5, "grip about 30 dia, 120 long", 13, "middle", fill="#fff")
# 4517 on the top flat of the right head, near the handle
rect(700, cy - 75 - 14, 50, 14, "#1e5aa8", "#123", 1.5, 2)
text(694, cy - 78, "4517", 12, "end", "bold", "#1e5aa8")
# half breadboard strapped on the far side of the right head (shown behind, dashed) + Nano
rect(735, cy - 40, 110, 70, "#f0f0f0", "#444", 1.5, 4, "6 4")
rect(752, cy - 25, 60, 24, "#2e7d32", "#1b5e20", 1.2, 3)
text(782, cy - 8, "Nano", 11, "middle", "bold", "#fff")
text(790, cy + 48, "half breadboard, rubber-banded to the head", 12, "middle", fill="#444")
# QT cable from 4517 to breadboard
a(f"<path d='M750,{cy-82} C790,{cy-82} 800,{cy-60} 790,{cy-40}' fill='none' stroke='#b58900' stroke-width='3'/>")
text(860, cy - 96, "4209 cable 150 mm", 12, fill="#8a6d00")
# USB cable out
a(f"<path d='M845,{cy-5} C900,{cy-5} 950,{cy+60} 1040,{cy+60}' fill='none' stroke='#222' stroke-width='3'/>")
text(1050, cy + 65, "USB-C 1-2 m to the laptop (power + recording)", 13, fill="#222")
# axes at the 4517
arrow(725, cy - 120, 640, cy - 120, "#c62828", "X along the grip, toward the grip")
arrow(725, cy - 120, 725, cy - 185, "#2e7d32", "Z up (component side)")
a(f"<circle cx='725' cy='{cy-120}' r='5' fill='#1565c0'/>"); text(738, cy - 126, "Y toward the viewer", 13, "start", "bold", "#1565c0")
label(740, cy - 82, 1000, cy - 150, "Foam tape on the top flat next to the grip, chip side up", "start")
text(30, 420, "Mass: dumbbell 0.9-1.4 kg + boards and cables about 80 g, matching the product target. Flat hex faces: tape holds, it does not roll, Z is the same every time.", 13.5, fill="#333")

if WITH_B:
    # ---------- Panel B: pipe + bottles ----------
    text(30, 480, "Option B (zero cost): a rigid rod about 30 dia (PVC, rolling pin, broom handle) with a 500 mL bottle taped to each end", 17, weight="bold", fill="#1a4d8f")
    cy = 680
    rect(150, cy - 70, 90, 180, "#9ec5e8", "#355", 2, 24); rect(840, cy - 70, 90, 180, "#9ec5e8", "#355", 2, 24)
    text(195, cy + 30, "500 mL", 12, "middle", fill="#123"); text(885, cy + 30, "500 mL", 12, "middle", fill="#123")
    rect(120, cy - 10, 840, 26, "#c8b68a", "#5a4a2a", 2, 13)   # rod
    text(540, cy + 8, "rod 40-50 cm, 12 cm free in the middle for the hand", 13, "middle", fill="#3a2e14")
    for x in (170, 220, 860, 910):
        line(x, cy - 72, x, cy + 112, "#222", 2, "3 3")      # tape bands
    text(195, cy + 128, "two turns of tape", 12, "middle", fill="#444"); text(885, cy + 128, "two turns of tape", 12, "middle", fill="#444")
    rect(760, cy - 10 - 14, 50, 14, "#1e5aa8", "#123", 1.5, 2); text(754, cy - 14, "4517", 12, "end", "bold", "#1e5aa8")
    rect(845, cy - 140, 110, 60, "#f0f0f0", "#444", 1.5, 4, "6 4"); rect(862, cy - 125, 60, 24, "#2e7d32", "#1b5e20", 1.2, 3); text(892, cy - 108, "Nano", 11, "middle", "bold", "#fff")
    text(930, cy - 172, "half breadboard on the bottle", 12, "middle", fill="#444")
    a(f"<path d='M810,{cy-20} C830,{cy-40} 840,{cy-90} 850,{cy-100}' fill='none' stroke='#b58900' stroke-width='3'/>")
    a(f"<path d='M955,{cy-110} C1000,{cy-110} 1020,{cy-40} 1080,{cy-40}' fill='none' stroke='#222' stroke-width='3'/>")
    text(1090, cy - 35, "USB-C to the laptop", 13, fill="#222")
    arrow(785, cy - 60, 700, cy - 60, "#c62828", "X toward the grip")
    arrow(785, cy - 60, 785, cy - 125, "#2e7d32", "Z up (chip side)")
    label(770, cy - 24, 600, cy - 150, "4517 on the rod by the right bottle; the rod is round: mark an up line, tape to it each time", "end")
    text(30, 830, "Mass: two bottles 1 kg + rod 0.2-0.4 kg, about 1.3 kg. Downsides: round rod, Z aligned by a pen mark (a few degrees off); grip feel differs from the product.", 13.5, fill="#333")

# ---------- Rules ----------
RY = 890 if WITH_B else 480
text(30, RY, "Rules for both options" if WITH_B else "Rules", 16, weight="bold")
rules = ["1. The 4517 must not move: foam tape plus a turn of tape over it. A loose sensor teaches the model its own rattle.",
         "2. Photograph the mounting as ml/figures/mounting-v1.jpg, write it into ml/data-protocol.md section 3, then never change it. The enclosure mounts the 4517 the same way so the data stays valid.",
         "3. Only the Nano on the breadboard; the four 4209 leads go into the holes beside its pins: 3V3, GND, A4, A5. No OLED, no pulse sensor.",
         "4. Before recording: 5 s at rest shows az about +9.8 and gx gy gz about 0 (Z up); two curls show gx far above gy and gz (X along the grip)."]
for i, r in enumerate(rules): text(30, RY + 26 + 20 * i, r, 13.5, fill="#333")
a("</svg>")
open(sys.argv[1], "w").write("\n".join(o)); print("ok")
