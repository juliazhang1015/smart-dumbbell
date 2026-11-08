# Generates smart-dumbbell.kicad_sch (KiCad 8 file format; opens in KiCad 8/9/10, imports into EasyEDA Pro).
# Run: python3 hardware/wiring/kicad/gen_kicad_sch.py hardware/wiring/kicad/smart-dumbbell.kicad_sch
# Geometry: schematic y grows downward; symbol-library y grows upward. All pins sit on the 2.54 mm grid.
import sys, uuid

def U(): return str(uuid.uuid4())
F = "(effects (font (size 1.27 1.27)))"
FH = "(effects (font (size 1.27 1.27)) hide)"
out = []
def add(s): out.append(s)

# ---------------- symbol library ----------------
def box_symbol(name, ref, value, w, pins_left, pins_right, desc=""):
    """pins_*: list of (number, name, etype, y_sym) with y in symbol coords (up positive). w = body half width."""
    n = max(len(pins_left), len(pins_right))
    ys = [p[3] for p in pins_left + pins_right]
    top = max(ys) + 2.54; bot = min(ys) - 2.54
    s = [f'(symbol "SD:{name}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)',
         f'(property "Reference" "{ref}" (at {-w} {round(top + 1.27, 2)} 0) (effects (font (size 1.27 1.27)) (justify left)))',
         f'(property "Value" "{value}" (at {-w} {round(bot - 2.54, 2)} 0) (effects (font (size 1.27 1.27)) (justify left)))',
         f'(property "Footprint" "" (at 0 0 0) {FH})', f'(property "Datasheet" "" (at 0 0 0) {FH})',
         f'(property "Description" "{desc}" (at 0 0 0) {FH})',
         f'(symbol "{name}_0_1" (rectangle (start {-w} {round(top, 2)}) (end {w} {round(bot, 2)}) (stroke (width 0.254) (type default)) (fill (type background))))',
         f'(symbol "{name}_1_1"']
    for num, nm, et, y in pins_left:
        s.append(f'(pin {et} line (at {round(-w - 2.54, 2)} {round(y, 2)} 0) (length 2.54) (name "{nm}" {F}) (number "{num}" {F}))')
    for num, nm, et, y in pins_right:
        s.append(f'(pin {et} line (at {round(w + 2.54, 2)} {round(y, 2)} 180) (length 2.54) (name "{nm}" {F}) (number "{num}" {F}))')
    s.append('))')
    return "\n".join(s)

def two_pin_symbol(name, ref, value, graphic, p1type="passive", p2type="passive", p1name="1", p2name="2"):
    return "\n".join([
        f'(symbol "SD:{name}" (pin_numbers hide) (pin_names (offset 0) hide) (exclude_from_sim no) (in_bom yes) (on_board yes)',
        f'(property "Reference" "{ref}" (at 0 2.54 0) {F})', f'(property "Value" "{value}" (at 0 -2.54 0) {F})',
        f'(property "Footprint" "" (at 0 0 0) {FH})', f'(property "Datasheet" "" (at 0 0 0) {FH})',
        f'(symbol "{name}_0_1" {graphic})',
        f'(symbol "{name}_1_1"',
        f'(pin {p1type} line (at -3.81 0 0) (length 1.27) (name "{p1name}" {F}) (number "1" {F}))',
        f'(pin {p2type} line (at 3.81 0 180) (length 1.27) (name "{p2name}" {F}) (number "2" {F}))', '))'])

def power_symbol(name, graphic):
    return "\n".join([
        f'(symbol "SD:{name}" (power) (pin_numbers hide) (pin_names (offset 0) hide) (exclude_from_sim no) (in_bom yes) (on_board yes)',
        f'(property "Reference" "#PWR" (at 0 0 0) {FH})', f'(property "Value" "{name}" (at 0 {3.81 if name != "GND" else -3.81} 0) {F})',
        f'(property "Footprint" "" (at 0 0 0) {FH})', f'(property "Datasheet" "" (at 0 0 0) {FH})',
        f'(symbol "{name}_0_1" {graphic})',
        f'(symbol "{name}_1_1" (pin power_in line (at 0 0 0) (length 0) hide (name "{name}" {F}) (number "1" {F})))', ')'])

P = 2.54
# Nano ESP32: 15 pins per side in physical header order (top view, USB up). Pin 1 = D13 at top left.
left_names = [("D13/SCK", "bidirectional"), ("+3V3", "power_out"), ("B0/BOOT0", "input"), ("A0", "bidirectional"), ("A1", "bidirectional"),
              ("A2", "bidirectional"), ("A3", "bidirectional"), ("A4/SDA", "bidirectional"), ("A5/SCL", "bidirectional"), ("A6", "bidirectional"),
              ("A7", "bidirectional"), ("VUSB", "power_in"), ("B1/BOOT1", "input"), ("GND", "power_out"), ("VIN", "power_in")]
right_names = [("D12/CIPO", "bidirectional"), ("D11/COPI", "bidirectional"), ("D10", "bidirectional"), ("D9", "bidirectional"), ("D8", "bidirectional"),
               ("D7", "bidirectional"), ("D6", "bidirectional"), ("D5", "bidirectional"), ("D4", "bidirectional"), ("D3", "bidirectional"),
               ("D2", "bidirectional"), ("GND", "passive"), ("RESET", "input"), ("RX0", "bidirectional"), ("TX1", "bidirectional")]
nano_left = [(i + 1, nm, et, 7 * P - i * P) for i, (nm, et) in enumerate(left_names)]
nano_right = [(16 + i, nm, et, 7 * P - i * P) for i, (nm, et) in enumerate(right_names)]

syms = [
    box_symbol("NanoESP32", "U", "Arduino Nano ESP32", 12.7, nano_left, nano_right, "ABX00083, pins in header order, USB at top"),
    box_symbol("IMU4517", "J", "Adafruit 4517 LSM6DSOX+LIS3MDL", 10.16, [], [(1, "V+/red", "power_in", P), (2, "SDA/blue", "bidirectional", 0), (3, "SCL/yellow", "bidirectional", -P), (4, "GND/black", "power_in", -2 * P)], "STEMMA QT cable 4209"),
    box_symbol("MAX30102", "J", "GY-MAX30102", 10.16, [], [(1, "VIN", "power_in", 2 * P), (2, "SDA", "bidirectional", P), (3, "SCL", "bidirectional", 0), (4, "INT", "output", -P), (5, "GND", "power_in", -2 * P)], "pulse oximeter module, 0.1in header"),
    box_symbol("OLED", "J", "OLED 0.96in SSD1306 128x64", 10.16, [], [(1, "VCC", "power_in", P), (2, "SDA", "bidirectional", 0), (3, "SCL", "bidirectional", -P), (4, "GND", "power_in", -2 * P)], "kit OLED, silkscreen order GND VCC SCL SDA"),
    box_symbol("GroveBuzzer", "BZ", "Grove Buzzer (optional)", 10.16, [(1, "SIG", "input", 1.5 * P), (2, "NC", "no_connect", 0.5 * P), (3, "VCC", "power_in", -0.5 * P), (4, "GND", "power_in", -1.5 * P)], [], "Seeed Grove Buzzer, not fitted in v1"),
    two_pin_symbol("SW_Push", "SW", "SW_Push",
        '(circle (center -2.032 0) (radius 0.508) (stroke (width 0) (type default)) (fill (type none))) (circle (center 2.032 0) (radius 0.508) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy -2.54 1.27) (xy 2.54 1.27)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 1.27) (xy 0 3.048)) (stroke (width 0) (type default)) (fill (type none)))'),
    two_pin_symbol("R", "R", "R", '(rectangle (start -2.54 1.016) (end 2.54 -1.016) (stroke (width 0.254) (type default)) (fill (type none)))'),
    two_pin_symbol("LED", "D", "LED",
        '(polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27) (xy 1.27 0) (xy -1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy -2.54 0) (xy -1.27 0)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 1.27 0) (xy 2.54 0)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy -0.508 1.778) (xy 0.508 3.048)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0.762 1.778) (xy 1.778 3.048)) (stroke (width 0) (type default)) (fill (type none)))',
        p1name="A", p2name="K"),
    power_symbol("GND", '(polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)) (stroke (width 0) (type default)) (fill (type none)))'),
    power_symbol("+3V3", '(polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy -0.762 1.27) (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none)))'),
]

# ---------------- placement (schematic coords, y down) ----------------
ROOT = U()
placed = []      # symbol instances
wires = []; junctions = []; labels = []; texts = []; ncs = []
def wire(x1, y1, x2, y2): wires.append((x1, y1, x2, y2))
def junc(x, y): junctions.append((x, y))
def nc(x, y): ncs.append((x, y))

def place(lib, ref, value, x, y, props=None, dnp=False, pins=None, rot=0):
    """x,y = symbol origin in schematic. Returns dict of pin number -> schematic (x,y) of the pin end."""
    placed.append((lib, ref, value, x, y, props or {}, dnp, pins or [], rot))
    return

def pin_pos(x0, y0, px, py):   # symbol coords -> schematic
    return (round(x0 + px, 3), round(y0 - py, 3))

# Nano U1
NX, NY = 152.4, 93.98
place("NanoESP32", "U1", "Arduino Nano ESP32", NX, NY, {"Reference": (NX - 12.7, NY - 20.32 - 1.27), "Value": (NX - 12.7, NY + 20.32 + 2.54)}, pins=[str(i) for i in range(1, 31)])
nano_pins = {}
for num, nm, et, y in nano_left:  nano_pins[num] = pin_pos(NX, NY, -15.24, y)
for num, nm, et, y in nano_right: nano_pins[num] = pin_pos(NX, NY, 15.24, y)
USED = {2, 8, 9, 14, 21, 23, 26, 27}
for num, (px, py) in nano_pins.items():
    if num not in USED: nc(px, py)

# Modules on the left: pin ends at x = MX + 12.7
MX = 60.96
def module(lib, ref, value, cy, pins, n):
    place(lib, ref, value, MX, cy, {"Reference": (MX - 10.16, cy - (n / 2 + 1) * P - 1.27), "Value": (MX - 10.16, cy + (n / 2 + 1) * P + 2.54)}, pins=[str(i) for i in range(1, n + 1)])
    return {num: pin_pos(MX, cy, 12.7, y) for num, nm, et, y in pins}

j2 = module("IMU4517", "J2", "Adafruit 4517 IMU", 43.18, [(1, "", "", P), (2, "", "", 0), (3, "", "", -P), (4, "", "", -2 * P)], 4)
j3 = module("MAX30102", "J3", "GY-MAX30102", 68.58, [(1, "", "", 2 * P), (2, "", "", P), (3, "", "", 0), (4, "", "", -P), (5, "", "", -2 * P)], 5)
j4 = module("OLED", "J4", "OLED SSD1306 0x3C", 91.44, [(1, "", "", P), (2, "", "", 0), (3, "", "", -P), (4, "", "", -2 * P)], 4)

SDA_X, SCL_X = 109.22, 104.14
PWR_X = MX + 12.7 + 5.08   # 78.74: where module power symbols sit
def pwr(kind, x, y): place(kind, "#PWR" + U()[:4], kind, x, y, pins=["1"])
def module_power(pins, vcc, gnd):
    x, y = pins[vcc]; wire(x, y, PWR_X, y); pwr("+3V3", PWR_X, y)
    x, y = pins[gnd]; wire(x, y, PWR_X, y); pwr("GND", PWR_X, y)
def module_i2c(pins, sda, scl):
    x, y = pins[sda]; wire(x, y, SDA_X, y)
    x, y = pins[scl]; wire(x, y, SCL_X, y)
module_power(j2, 1, 4); module_i2c(j2, 2, 3)
module_power(j3, 1, 5); module_i2c(j3, 2, 3); nc(*j3[4])
module_power(j4, 1, 4); module_i2c(j4, 2, 3)
# rails
sda_ys = [j2[2][1], j3[2][1], j4[2][1]]; scl_ys = [j2[3][1], j3[3][1], j4[3][1]]
a4 = nano_pins[8]; a5 = nano_pins[9]
wire(SDA_X, min(sda_ys), SDA_X, a4[1]); wire(SDA_X, a4[1], a4[0], a4[1])
wire(SCL_X, min(scl_ys), SCL_X, a5[1]); wire(SCL_X, a5[1], a5[0], a5[1])
for y in sda_ys:
    if y != min(sda_ys): junc(SDA_X, y)
for y in scl_ys:
    if y != min(scl_ys): junc(SCL_X, y)
labels.append(("SDA", SDA_X, (sda_ys[0] + sda_ys[1]) / 2, 90)); labels.append(("SCL", SCL_X, (scl_ys[0] + scl_ys[1]) / 2 + 5.08, 90))
# Nano power
x, y = nano_pins[2]; wire(x, y, x - 5.08, y); pwr("+3V3", x - 5.08, y)
x, y = nano_pins[14]; wire(x, y, x - 5.08, y); pwr("GND", x - 5.08, y)
x, y = nano_pins[27]; wire(x, y, x + 5.08, y); pwr("GND", x + 5.08, y)
# SW1 on D2
x, y = nano_pins[26]; wire(x, y, x + 12.7, y)
SWX = x + 12.7 + 3.81; place("SW_Push", "SW1", "start/pause/end", SWX, y, {"Reference": (SWX - 2.54, y - 5.08), "Value": (SWX - 8.89, y + 3.81)}, pins=["1", "2"])
wire(SWX + 3.81, y, SWX + 3.81 + 5.08, y); pwr("GND", SWX + 3.81 + 5.08, y)
# R1 + LED1 on D7
x, y = nano_pins[21]; wire(x, y, x + 7.62, y)
RX = x + 7.62 + 3.81; place("R", "R1", "220", RX, y, {"Reference": (RX, y - 2.54), "Value": (RX, y + 2.54)}, pins=["1", "2"])
wire(RX + 3.81, y, RX + 3.81 + 5.08, y)
LX = RX + 3.81 + 5.08 + 3.81; place("LED", "LED1", "red/yellow", LX, y, {"Reference": (LX - 2.54, y - 5.08), "Value": (LX - 8.89, y + 3.81)}, pins=["1", "2"])
wire(LX + 3.81, y, LX + 3.81 + 5.08, y); pwr("GND", LX + 3.81 + 5.08, y)
# Buzzer on D5 (DNP)
x, y = nano_pins[23]
BX, BY = 215.9, 124.46
place("GroveBuzzer", "BZ1", "Grove Buzzer - NOT FITTED (USE_BUZZER 0)", BX, BY, {"Reference": (BX - 10.16, BY - 3 * P - 1.27), "Value": (BX - 10.16, BY + 3 * P + 2.54)}, dnp=True, pins=["1", "2", "3", "4"])
bz = {n: pin_pos(BX, BY, -12.7, yy) for n, yy in ((1, 1.5 * P), (2, 0.5 * P), (3, -0.5 * P), (4, -1.5 * P))}
wire(x, y, bz[1][0], y); wire(bz[1][0], y, bz[1][0], bz[1][1])
nc(*bz[2])
wire(bz[3][0], bz[3][1], bz[3][0] - 5.08, bz[3][1]); pwr("+3V3", bz[3][0] - 5.08, bz[3][1])
wire(bz[4][0], bz[4][1], bz[4][0] - 5.08, bz[4][1]); pwr("GND", bz[4][0] - 5.08, bz[4][1])

# Notes
texts.append((30.48, 163.83, "Notes\\n"
    "1. Power: Nano ESP32 only from USB-C (INIU SnapGo P81 power bank). The Nano 3V3 pin feeds every module. VIN and VUSB unused.\\n"
    "2. One I2C bus, 400 kHz: LSM6DSOX 0x6A, LIS3MDL 0x1C (unused), MAX30102 0x57, SSD1306 0x3C. Scanned together 2026-11-03; all four ran in firmware/app 2026-11-06.\\n"
    "3. Pull-ups: 4517 has 10k to 3.3 V; GY-MAX30102 has 4.7k to its own 1.8 V rail. Measure SDA/SCL high level; below 2.5 V remove the MAX30102 pull-ups.\\n"
    "4. SW1: one kit pushbutton to GND, INPUT_PULLUP on D2. Short press start/pause/resume, hold 1.5 s end (firmware/app). Tested 2026-11-06.\\n"
    "5. LED1 on D7 through 220 ohm; use a red or yellow LED at 3.3 V. BZ1 is optional: firmware/app compiles with USE_BUZZER 0, D5 held LOW.\\n"
    "6. 4517 pins follow the 4209 STEMMA QT cable colours. MAX30102 INT and 4517 INT not wired (polling). D8/D9 reserved for them.\\n"
    "Source: hardware/wiring/README.md, firmware/app/app.ino. Redrawn in KiCad from Julia's EasyEDA V2.0 (2026-11-08); regenerate with gen_kicad_sch.py."))

# ---------------- emit ----------------
add('(kicad_sch (version 20231120) (generator "eeschema") (generator_version "8.0")')
add(f'(uuid "{ROOT}")')
add('(paper "A4")')
add('(title_block (title "Smart Dumbbell - wiring v2.1") (date "2026-11-08") (rev "V2.1") (company "ECE 198 Group 57") (comment 1 "Drawn: Julia Zhang (EasyEDA V2.0, 2026-11-08). KiCad version: Hanson He.") (comment 2 "Single button, buzzer not fitted. Bench build on half breadboard, Nano off-board."))')
add('(lib_symbols'); out.extend(syms); add(')')
for x1, y1, x2, y2 in wires:
    add(f'(wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid "{U()}"))')
for x, y in junctions:
    add(f'(junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid "{U()}"))')
for x, y in ncs:
    add(f'(no_connect (at {x} {y}) (uuid "{U()}"))')
for name, x, y, rot in labels:
    add(f'(label "{name}" (at {x} {y} {rot}) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{U()}"))')
for x, y, t in texts:
    add(f'(text "{t}" (exclude_from_sim no) (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{U()}"))')
for lib, ref, value, x, y, props, dnp, pins, rot in placed:
    is_pwr = lib in ("GND", "+3V3")
    uid = U()
    add(f'(symbol (lib_id "SD:{lib}") (at {x} {y} {rot}) (unit 1) (exclude_from_sim no) (in_bom {"no" if is_pwr else "yes"}) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid "{uid}")')
    rx, ry = props.get("Reference", (x, y - 2.54)); vx, vy = props.get("Value", (x, y + 2.54))
    if is_pwr: vx, vy = x, (y - 4.445 if lib == "+3V3" else y + 4.445)
    hide_ref = " hide" if is_pwr else ""
    add(f'(property "Reference" "{ref}" (at {rx} {ry} 0) (effects (font (size 1.27 1.27)) (justify left){hide_ref}))')
    add(f'(property "Value" "{value}" (at {vx} {vy} 0) (effects (font (size 1.27 1.27)){"" if is_pwr else " (justify left)"}))')
    add(f'(property "Footprint" "" (at {x} {y} 0) {FH}) (property "Datasheet" "" (at {x} {y} 0) {FH})')
    for p in pins: add(f'(pin "{p}" (uuid "{U()}"))')
    add(f'(instances (project "smart-dumbbell" (path "/{ROOT}" (reference "{ref}") (unit 1)))))')
add('(sheet_instances (path "/" (page "1")))')
add(')')
open(sys.argv[1], "w").write("\n".join(out) + "\n")
print("wrote", sys.argv[1], len(placed), "symbols", len(wires), "wires")
