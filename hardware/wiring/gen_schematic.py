# Generates the current schematic (v1.2). Run: python3 hardware/wiring/gen_schematic.py hardware/wiring/schematic-v1.2.svg
# schematic-v1.svg (three buttons + Grove buzzer, 2026-11-04) is kept as drawn; it is no longer produced by this script.
import sys
W, H = 1500, 1080
F = "Helvetica, Arial, sans-serif"
C_GND, C_3V3, C_SCL, C_SDA, C_SIG, C_TXT, C_SUB = "#111", "#c62828", "#b58900", "#1565c0", "#333", "#111", "#555"
out = []
def add(s): out.append(s)
def text(x, y, s, size=12, anchor="start", weight="normal", fill=C_TXT, family=F, extra=""):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    add(f"<text x='{x}' y='{y}' font-size='{size}' text-anchor='{anchor}' font-weight='{weight}' fill='{fill}' font-family='{family}' {extra}>{s}</text>")
def line(x1, y1, x2, y2, stroke=C_SIG, w=1.8, dash=None):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    add(f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{stroke}' stroke-width='{w}' stroke-linecap='round'{d}/>")
def poly(pts, stroke=C_SIG, w=1.8, fill="none", dash=None):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    add(f"<polyline points='{' '.join(f'{x},{y}' for x, y in pts)}' fill='{fill}' stroke='{stroke}' stroke-width='{w}' stroke-linejoin='round' stroke-linecap='round'{d}/>")
def dot(x, y, c=C_SIG): add(f"<circle cx='{x}' cy='{y}' r='3.6' fill='{c}'/>")
def box(x, y, w, h, fill="#f7f7f7", stroke="#333", rx=5, dash=None):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    add(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{rx}' fill='{fill}' stroke='{stroke}' stroke-width='1.5'{d}/>")
def gnd_symbol(x, y, c=C_GND, dash=None):  # stem down from (x,y), then three bars
    line(x, y, x, y + 14, c, 1.8, dash); line(x - 12, y + 14, x + 12, y + 14, c, 2)
    line(x - 8, y + 19, x + 8, y + 19, c, 2); line(x - 4, y + 24, x + 4, y + 24, c, 2)
def v33_flag(x, y, dash=None):  # stem up from (x,y), bar and label
    line(x, y, x, y - 14, C_3V3, 1.8, dash); line(x - 10, y - 14, x + 10, y - 14, C_3V3, 2.2)
    text(x, y - 19, "3V3", 11, "middle", "bold", C_3V3)
def resistor(x1, x2, y, label):  # horizontal IEC rectangle
    w = x2 - x1; line(x1, y, x1 + 10, y); box(x1 + 10, y - 7, w - 20, 14, "white", C_SIG, 1); line(x2 - 10, y, x2, y)
    text((x1 + x2) / 2, y - 12, label, 11, "middle")
def led(x, y, label):  # anode at (x,y) pointing right, cathode at x+36
    line(x, y, x + 10, y); add(f"<polygon points='{x+10},{y-9} {x+10},{y+9} {x+26},{y}' fill='white' stroke='{C_SIG}' stroke-width='1.8'/>")
    line(x + 26, y - 9, x + 26, y + 9); line(x + 26, y, x + 36, y)
    for dx in (14, 20):
        line(x + dx, y - 10, x + dx + 7, y - 18, C_SIG, 1.4); add(f"<polygon points='{x+dx+7},{y-18} {x+dx+2},{y-17} {x+dx+6},{y-13}' fill='{C_SIG}'/>")
    text(x + 18, y + 24, label, 11, "middle")
def switch(x, y, label, sub):  # NO pushbutton from (x,y) to (x+60,y)
    line(x, y, x + 14, y); line(x + 46, y, x + 60, y)
    add(f"<circle cx='{x+16}' cy='{y}' r='3' fill='white' stroke='{C_SIG}' stroke-width='1.6'/>")
    add(f"<circle cx='{x+44}' cy='{y}' r='3' fill='white' stroke='{C_SIG}' stroke-width='1.6'/>")
    line(x + 16, y - 10, x + 44, y - 10, C_SIG, 2); line(x + 30, y - 10, x + 30, y - 20, C_SIG, 1.6)
    text(x + 30, y - 26, label, 11, "middle", "bold"); text(x + 30, y + 18, sub, 10.5, "middle", "normal", C_SUB)

add(f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>")
add(f"<rect width='{W}' height='{H}' fill='white'/>")
text(20, 30, "Smart dumbbell - schematic v1.2 (2026-11-08)", 19, weight="bold")
text(20, 50, "Modules as photographed 2026-11-04. I2C section: all four devices scanned 2026-11-03 (0x1C 0x3C 0x57 0x6A) and run together by firmware/app on 2026-11-06. SW1 tested 2026-11-06; LED wired, not yet observed.", 11.5, fill=C_SUB)
text(20, 66, "Pin names are the Arduino names printed on the Nano ESP32 header. All logic is 3.3 V. A dot is a junction; a crossing without a dot is not a connection. Dashed = not fitted. Change from v1: one button (SW1), buzzer not fitted.", 11.5, fill=C_SUB)

# ---------- Nano ESP32 ----------
NX, NY, NW, NH = 640, 180, 240, 640
box(NX, NY, NW, NH, "#e8f0fe")
text(NX + NW / 2, NY + 22, "Arduino Nano ESP32", 14, "middle", "bold")
text(NX + NW / 2, NY + 40, "ABX00083, u-blox NORA-W106 (ESP32-S3)", 10.5, "middle", fill=C_SUB)
text(NX + NW / 2, NY + 56, "on-board 3.3 V LDO feeds the 3V3 pin", 10.5, "middle", fill=C_SUB)

# USB-C from power bank
PBX, PBY, PBW, PBH = 660, 86, 200, 56
box(PBX, PBY, PBW, PBH, "#fff8e1")
text(PBX + PBW / 2, PBY + 22, "INIU SnapGo P81 power bank", 12, "middle", "bold")
text(PBX + PBW / 2, PBY + 40, "5 V over its built-in USB-C cable", 10.5, "middle", fill=C_SUB)
line(760, PBY + PBH, 760, NY, C_3V3, 2.2)
text(766, NY - 8, "USB-C (VBUS)", 11, fill=C_3V3)

# Left pins: order chosen so rails fan out without crossing each other at the Nano
LP = [("GND", 260, C_GND, 420), ("3V3", 300, C_3V3, 470), ("A5 / SCL", 340, C_SCL, 520), ("A4 / SDA", 380, C_SDA, 570)]
RAIL_BOTTOM = 1030
for name, y, c, rx in LP:
    line(NX, y, NX - 30, y, c); text(NX + 8, y + 4, name, 12, "start", "bold")
    line(NX - 30, y, rx, y, c); line(rx, y, rx, RAIL_BOTTOM, c, 2.2)
    dot(rx, y, c)
text(420, 1052, "GND", 11, "middle", "bold", C_GND); text(470, 1052, "3V3", 11, "middle", "bold", C_3V3)
text(520, 1052, "SCL", 11, "middle", "bold", C_SCL); text(570, 1052, "SDA", 11, "middle", "bold", C_SDA)
RAIL = {"GND": (420, C_GND), "3V3": (470, C_3V3), "SCL": (520, C_SCL), "SDA": (570, C_SDA)}

# Right pins. Solid stubs: D2 (SW1) and D7 (LED). Dashed: free or reserved.
RP = [("D2", 260), ("D3", 330), ("D4", 400), ("D5", 490), ("D7", 640), ("D8", 720), ("D9", 760)]
for name, y in RP:
    text(NX + NW - 8, y + 4, name, 12, "end", "bold")
for y in (260, 640):
    line(NX + NW, y, NX + NW + 30, y)
for y, note in [(330, "free (SW2 Pause removed; firmware/app uses one button)"), (400, "free (SW3 End removed)"),
                (720, "reserved: GY-MAX30102 INT (not wired, polling used)"), (760, "reserved: 4517 INT1 data-ready (not wired)")]:
    line(NX + NW, y, NX + NW + 30, y, C_SIG, 1.5, "4 4"); text(NX + NW + 36, y + 4, note, 10.5, fill=C_SUB)

# ---------- I2C modules on the left ----------
MX, MW = 60, 290
def module(y0, h, title, sub, pins, notes):
    box(MX, y0, MW, h, "#f3f3f3")
    text(MX + 10, y0 + 20, title, 13, "start", "bold"); text(MX + 10, y0 + 36, sub, 10.5, fill=C_SUB)
    for i, (pname, net, y) in enumerate(pins):
        rx, c = RAIL[net]
        text(MX + MW - 8, y + 4, pname, 12, "end", "bold")
        line(MX + MW, y, rx, y, c); dot(rx, y, c)
    for j, n in enumerate(notes):
        text(MX + 10, y0 + h - 8 - 14 * (len(notes) - 1 - j), n, 10, fill=C_SUB)

module(430, 195, "Adafruit 4517  LSM6DSOX + LIS3MDL", "STEMMA QT cable 4209 (either JST connector)",
       [("GND  black", "GND", 490), ("V+  red", "3V3", 520), ("SDA  blue", "SDA", 550), ("SCL  yellow", "SCL", 580)],
       ["I2C 0x6A (LSM6DSOX), 0x1C (LIS3MDL, unused)", "10 k pull-ups to 3.3 V on board"])
module(645, 215, "GY-MAX30102 pulse oximeter", "0.1 in header, pins per silkscreen",
       [("VIN", "3V3", 705), ("GND", "GND", 735), ("SCL", "SCL", 765), ("SDA", "SDA", 795)],
       ["I2C 0x57;  INT pin left open (see D8)", "4.7 k pull-ups to on-board 1.8 V: see note 3"])
module(880, 165, "Kit OLED 0.96 in  SSD1306 128x64", "pin order GND VCC SCL SDA (silkscreen, photo 2026-11-04)",
       [("GND", "GND", 940), ("VCC", "3V3", 970), ("SCL", "SCL", 1000), ("SDA", "SDA", 1030)],
       ["I2C 0x3C"])
# MAX30102 INT stub
text(MX + MW - 8, 829, "INT", 12, "end", "bold", C_SUB); line(MX + MW, 825, MX + MW + 20, 825, C_SUB, 1.4, "3 3")
text(MX + MW + 26, 829, "n.c.", 10.5, fill=C_SUB)

# ---------- Right side: SW1, optional buzzer, LED ----------
SX = NX + NW + 30  # 910
line(SX, 260, 1000, 260); switch(1000, 260, "SW1", "kit pushbutton, to GND"); line(1060, 260, 1100, 260); gnd_symbol(1100, 260)
for i, s in enumerate(["INPUT_PULLUP on D2; no external resistor. Pressed = LOW.",
                       "Short press: start / pause / resume.  Hold 1.5 s: end.",
                       "Tested 2026-11-06 with firmware/app (EVENT lines on serial)."]):
    text(1130, 250 + 16 * i, s, 10.5, fill=C_SUB)

# Buzzer: not fitted in v1.2, D5 reserved. Drawn dashed so the pin assignment survives if the team adds one back.
GX, GY, GW, GH = 1090, 430, 290, 200
box(GX, GY, GW, GH, "#fbfbfb", "#777", 5, "6 4")
text(GX + 10, GY + 20, "Buzzer - NOT FITTED (optional)", 13, "start", "bold", "#555")
text(GX + 10, GY + 36, "Grove Buzzer (Seeed) or kit active buzzer module", 10.5, fill=C_SUB)
gp = [("SIG", 490), ("VCC", 550), ("GND", 580)]
for pname, y in gp:
    text(GX + 10, y + 4, pname, 12, "start", "bold", "#555")
line(NX + NW, 490, GX, 490, C_SIG, 1.5, "4 4")          # D5 -> SIG, dashed
text(NX + NW + 36, 484, "reserved: buzzer SIG", 10.5, fill=C_SUB)
line(GX, 550, 1040, 550, C_3V3, 1.8, "4 4"); v33_flag(1040, 550, "4 4")
line(GX, 580, 1040, 580, C_GND, 1.8, "4 4"); gnd_symbol(1040, 580, C_GND, "4 4")
for i, s in enumerate(["firmware/app: USE_BUZZER 0, D5 held LOW.", "If fitted: HIGH on SIG = sound; Grove needs a",
                       "Grove-to-male-jumper cable (Seeed 110990210)."]):
    text(GX + 10, GY + GH - 36 + 14 * i, s, 10, fill=C_SUB)

# LED + resistor on D7
line(SX, 640, 960, 640); resistor(960, 1050, 640, "R1  220 ohm"); led(1060, 640, "LED1 (kit, red or yellow)"); line(1096, 640, 1165, 640); gnd_symbol(1165, 640)
text(960, 690, "Wired on the bench 2026-11-06, not yet seen lit.", 10.5, fill=C_SUB)
text(960, 704, "Alternative: on-board RGB LED (LED_RED etc., active low) and drop this net.", 10.5, fill=C_SUB)

# Notes box
bx, by, bw, bh = 920, 800, 480, 232
box(bx, by, bw, bh, "#fffdf5", "#999", 4)
text(bx + 12, by + 22, "Notes", 12.5, "start", "bold")
notes = [
    "1. Power: Nano only from USB-C. No VIN, no bare LiPo. 3V3 pin supplies every module.",
    "2. One I2C bus at 400 kHz: 0x6A, 0x1C, 0x57, 0x3C. Scanned together 2026-11-03 (bring-up 07);",
    "   all four ran together in firmware/app 2026-11-06. Adafruit_SSD1306 defaults drop the bus to",
    "   100 kHz after each display call; firmware/app sets 400 kHz for clkDuring and clkAfter.",
    "3. Bus high level: 4517 10 k to 3.3 V with MAX30102 4.7 k to 1.8 V alone is about 2.3 V, under",
    "   the ESP32-S3 V_IH (about 2.5 V); the OLED's own pull-ups raise it. Works so far but is not",
    "   measured. Meter SDA/SCL high; below 2.5 V, remove or move the MAX30102 pull-ups.",
    "4. Button: SW1 on D2 only, one leg to the pin, the other to GND. Debounce in firmware.",
    "5. Pins from firmware/app/app.ino: PIN_BTN D2, PIN_BUZZ D5 (compiled out), PIN_LED D7.",
    "6. Not drawn: UNO R4 bench board, ADXL335 backup, LIS3MDL magnetometer (same board, unused).",
    "   D6 free. Bench build: Nano off-board, half breadboard as hub (halfboard-v1.svg).",
    "Source: hardware/wiring/README.md net list + firmware/app. Regenerate from gen_schematic.py.",
]
for i, n in enumerate(notes):
    text(bx + 12, by + 42 + 16 * i, n, 10.5, fill="#333")
add("</svg>")
open(sys.argv[1], "w").write("\n".join(out) + "\n")
print("wrote", sys.argv[1], len("\n".join(out)), "bytes")
