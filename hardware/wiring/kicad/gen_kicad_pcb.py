# Generates perfboard-v1.kicad_pcb: the 30 x 70 mm perfboard hub drawn as a KiCad board (KiCad 8 file format; opens in 8/9/10).
# Run: python3 hardware/wiring/kicad/gen_kicad_pcb.py hardware/wiring/kicad/perfboard-v1.kicad_pcb
# Same pads and nets as ../gen_perfboard.py: change both together.
# Reading the board: every perfboard hole is one pad named column + row (B8). F.Cu tracks are the insulated jumper wires
# on the component side, B.Cu tracks are bare wire / solder bridges on the solder side. Sockets and R1 are drawn as
# outline + 3D model only; the pads they solder into belong to the perfboard footprint.
# Not a fabrication file. Hole grid 10 x 24 and the Nano outline are catalogue values, not measured.
import sys, uuid

def U(): return str(uuid.uuid4())
COLS = "ABCDEFGHIJ"
X0, Y0, P = 3.57, 5.79, 2.54
BW, BL = 30.0, 70.0
OX, OY = 100.0, 60.0                      # board origin on the sheet
def X(c): return X0 + P * COLS.index(c)
def Y(r): return Y0 + P * (r - 1)          # r may be fractional: 17.5 is the gap between rows 17 and 18
def f(v): return f"{v:.3f}".rstrip("0").rstrip(".")

NETS = ["", "+3V3", "GND", "SDA", "SCL", "D2_SW1", "D7_LED", "LED_A"]
PADNET = {}
def assign(net, pads):
    for p in pads:
        assert p not in PADNET, p
        PADNET[p] = net
assign("+3V3", ["C2", "B2"] + [f"A{r}" for r in range(18, 23)])
assign("SDA", ["C8", "B8"] + [f"B{r}" for r in range(18, 23)])
assign("SCL", ["C9", "B9"] + [f"C{r}" for r in range(18, 23)])
assign("GND", ["C14"] + [f"D{r}" for r in range(14, 24)] + [f"{c}23" for c in "EFGHI"])
assign("D2_SW1", ["I11", "J11", "G21", "G22"])
assign("D7_LED", ["I6", "J6", "J17", "J18"])
assign("LED_A", ["J22", "I22"])

out = []
def add(s): out.append(s)
FONT = "(effects (font (size 1 1) (thickness 0.15)){j})"
def gtext(s, x, y, layer="Cmts.User", just="", size=1.0, ang=0):
    j = f" (justify {just})" if just else ""
    add(f'(gr_text "{s}" (at {f(OX + x)} {f(OY + y)} {ang}) (layer "{layer}") (uuid "{U()}") (effects (font (size {size} {size}) (thickness {f(size * 0.15)})){j}))')
def grect(x1, y1, x2, y2, layer, w=0.1, typ="default"):
    add(f'(gr_rect (start {f(OX + x1)} {f(OY + y1)}) (end {f(OX + x2)} {f(OY + y2)}) (stroke (width {w}) (type {typ})) (fill none) (layer "{layer}") (uuid "{U()}"))')
def gline(x1, y1, x2, y2, layer, w=0.1, typ="default"):
    add(f'(gr_line (start {f(OX + x1)} {f(OY + y1)}) (end {f(OX + x2)} {f(OY + y2)}) (stroke (width {w}) (type {typ})) (layer "{layer}") (uuid "{U()}"))')
def track(pts, net, layer, w):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        add(f'(segment (start {f(OX + x1)} {f(OY + y1)}) (end {f(OX + x2)} {f(OY + y2)}) (width {w}) (layer "{layer}") (net {NETS.index(net)}) (uuid "{U()}"))')
def pad(c, r): return (X(c), Y(r))
def prop(name, val, x, y, layer="F.Fab", hide=False):
    h = " (hide yes)" if hide else ""
    return f'(property "{name}" "{val}" (at {f(x)} {f(y)} 0) (layer "{layer}"){h} (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))'

add('(kicad_pcb (version 20240108) (generator "pcbnew") (generator_version "8.0")')
add('(general (thickness 1.6) (legacy_teardrops no))')
add('(paper "A4")')
add('(title_block (title "Smart Dumbbell - perfboard hub v1 (proposal)") (date "2026-11-16") (rev "v1") (company "ECE 198 Group 57")'
    ' (comment 1 "Layout proposal, not built or tested. Nets follow schematic v1.2 / KiCad sch V2.1 and firmware/app.")'
    ' (comment 2 "F.Cu = insulated jumper wires, component side. B.Cu = bare wire and solder bridges, solder side."))')
add('(layers (0 "F.Cu" signal) (31 "B.Cu" signal) (32 "B.Adhes" user "B.Adhesive") (33 "F.Adhes" user "F.Adhesive") (34 "B.Paste" user) (35 "F.Paste" user)'
    ' (36 "B.SilkS" user "B.Silkscreen") (37 "F.SilkS" user "F.Silkscreen") (38 "B.Mask" user) (39 "F.Mask" user) (40 "Dwgs.User" user "User.Drawings")'
    ' (41 "Cmts.User" user "User.Comments") (42 "Eco1.User" user "User.Eco1") (43 "Eco2.User" user "User.Eco2") (44 "Edge.Cuts" user) (45 "Margin" user)'
    ' (46 "B.CrtYd" user "B.Courtyard") (47 "F.CrtYd" user "F.Courtyard") (48 "B.Fab" user) (49 "F.Fab" user))')
add('(setup (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no))')
for i, n in enumerate(NETS): add(f'(net {i} "{n}")')

# ---------------- the perfboard itself: 240 plated holes + 4 mounting holes ----------------
fp = [f'(footprint "SD:Perfboard_30x70_10x24" (layer "F.Cu") (uuid "{U()}") (at {f(OX)} {f(OY)})',
      '(descr "Double-sided 2.54 mm perfboard 30 x 70 mm, 10 x 24 plated holes (catalogue grid, count the real board)")',
      prop("Reference", "PB1", 15, -7.5), prop("Value", "Perfboard 30x70, 10x24 holes", 15, BL + 2.5),
      prop("Footprint", "", 0, 0, hide=True), prop("Datasheet", "", 0, 0, hide=True), prop("Description", "", 0, 0, hide=True),
      '(attr through_hole)',
      f'(fp_rect (start 0 0) (end {f(BW)} {f(BL)}) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd") (uuid "{U()}"))']
for c in COLS:
    for r in range(1, 25):
        name = f"{c}{r}"; net = PADNET.get(name)
        n = f' (net {NETS.index(net)} "{net}")' if net else ""
        fp.append(f'(pad "{name}" thru_hole circle (at {f(X(c))} {f(Y(r))}) (size 1.7 1.7) (drill 1) (layers "*.Cu" "*.Mask") (remove_unused_layers no){n} (uuid "{U()}"))')
for cx, cy in ((2.3, 2.3), (BW - 2.3, 2.3), (2.3, BL - 2.3), (BW - 2.3, BL - 2.3)):
    fp.append(f'(pad "" np_thru_hole circle (at {f(cx)} {f(cy)}) (size 2 2) (drill 2) (layers "*.Cu" "*.Mask") (uuid "{U()}"))')
fp.append(')')
add("\n".join(fp))

# ---------------- parts that sit in the holes: outline + 3D model, no pads of their own ----------------
M = "${KICAD10_3DMODEL_DIR}"
def part(ref, value, lib, model, c, r, ang, graphics, refat):
    x, y = pad(c, r)
    s = [f'(footprint "{lib}" (layer "F.Cu") (uuid "{U()}") (at {f(OX + x)} {f(OY + y)} {ang})',
         prop("Reference", ref, refat[0], refat[1]), prop("Value", value, 0, 0, hide=True),
         prop("Footprint", "", 0, 0, hide=True), prop("Datasheet", "", 0, 0, hide=True), prop("Description", "", 0, 0, hide=True),
         '(attr through_hole)'] + graphics
    s.append(f'(model "{M}/{model}" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))')
    s.append(')')
    add("\n".join(s))
def socket_gfx(n):
    return [f'(fp_rect (start -1.27 -1.27) (end 1.27 {f((n - 1) * P + 1.27)}) (stroke (width 0.12) (type default)) (fill none) (layer "F.Fab") (uuid "{U()}"))',
            f'(fp_rect (start -1.27 -1.27) (end 1.27 {f((n - 1) * P + 1.27)}) (stroke (width 0.12) (type default)) (fill none) (layer "F.SilkS") (uuid "{U()}"))']
SOCK = "Connector_PinSocket_2.54mm"
part("J10", "Nano socket JP1 (1x15)", f"{SOCK}:PinSocket_1x15_P2.54mm_Vertical", f"{SOCK}.3dshapes/PinSocket_1x15_P2.54mm_Vertical.step", "C", 1, 0, socket_gfx(15), (0, -2.6))
part("J11", "Nano socket JP2 (1x15)", f"{SOCK}:PinSocket_1x15_P2.54mm_Vertical", f"{SOCK}.3dshapes/PinSocket_1x15_P2.54mm_Vertical.step", "I", 1, 0, socket_gfx(15), (0, -2.6))
part("J1", "IMU 4209 cable (1x4)", f"{SOCK}:PinSocket_1x04_P2.54mm_Vertical", f"{SOCK}.3dshapes/PinSocket_1x04_P2.54mm_Vertical.step", "A", 19, 90, socket_gfx(4), (-2.4, 0))
part("R1", "220R", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
     "Resistor_THT.3dshapes/R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal.step", "J", 18, -90,
     [f'(fp_rect (start 1.93 -1.25) (end 8.23 1.25) (stroke (width 0.12) (type default)) (fill none) (layer "{L}") (uuid "{U()}"))' for L in ("F.Fab", "F.SilkS")], (5.08, 2.4))

# ---------------- board outline, Nano outline ----------------
grect(0, 0, BW, BL, "Edge.Cuts", 0.1)
NXC = (X("C") + X("I")) / 2
NY0, NY1 = Y(1) - 4.72, Y(15) + 4.72
grect(NXC - 9, NY0, NXC + 9, NY1, "Dwgs.User", 0.15, "dash")
grect(NXC - 4.5, NY0 - 1.6, NXC + 4.5, NY0 + 5.8, "Dwgs.User", 0.15, "dash")
gtext("USB-C", NXC, NY0 + 2.2, "Dwgs.User", size=0.9)
gtext("Nano ESP32 in sockets J10/J11 (45 x 18 assumed)", NXC, Y(8), "Dwgs.User", size=0.9, ang=90)

# ---------------- jumper wires, component side (F.Cu, 0.3 mm so they pass between pads) ----------------
WF = 0.3
track([pad("B", 2), (4.84, Y(2.5)), (2.0, Y(2.5)), (1.2, Y(2.5) + 0.8), (1.2, Y(18) - 0.8), (2.0, Y(18)), pad("A", 18)], "+3V3", "F.Cu", WF)
track([pad("B", 8), (4.84, Y(8.5)), (4.84, Y(17.5)), pad("B", 18)], "SDA", "F.Cu", WF)
track([pad("B", 9), (7.38, Y(9.5)), (7.38, Y(17.5)), pad("C", 18)], "SCL", "F.Cu", WF)
track([pad("J", 6), (27.8, Y(6)), (28.7, Y(6) + 0.9), (28.7, Y(17) - 0.9), (27.8, Y(17)), pad("J", 17)], "D7_LED", "F.Cu", WF)
track([pad("J", 11), (27.5, Y(11)), (27.9, Y(11) + 0.4), (27.9, Y(16.5) - 0.4), (27.5, Y(16.5)), (20.08, Y(16.5)), (20.08, Y(20.5)), pad("G", 21)], "D2_SW1", "F.Cu", WF)

# ---------------- bare wire and solder bridges, solder side (B.Cu) ----------------
WB = 0.8
for a, b, net in ((("B", 2), ("C", 2), "+3V3"), (("B", 8), ("C", 8), "SDA"), (("B", 9), ("C", 9), "SCL"), (("C", 14), ("D", 14), "GND"),
                  (("J", 6), ("I", 6), "D7_LED"), (("J", 11), ("I", 11), "D2_SW1"), (("J", 17), ("J", 18), "D7_LED"),
                  (("J", 22), ("I", 22), "LED_A"), (("G", 21), ("G", 22), "D2_SW1")):
    track([pad(*a), pad(*b)], net, "B.Cu", WB)
track([pad("A", 18), pad("A", 22)], "+3V3", "B.Cu", WB)
track([pad("B", 18), pad("B", 22)], "SDA", "B.Cu", WB)
track([pad("C", 18), pad("C", 22)], "SCL", "B.Cu", WB)
track([pad("D", 14), pad("D", 23), pad("I", 23)], "GND", "B.Cu", WB)

# ---------------- annotations (User.Comments) ----------------
for c in COLS: gtext(c, X(c), -3.4)
for r in range(1, 25): gtext(str(r), -1.8, Y(r), just="right", size=0.9)
for r, s in ((2, "3V3"), (8, "A4 SDA"), (9, "A5 SCL"), (14, "GND")): gtext(s, X("D") - 0.9, Y(r), just="left", size=0.8)
for r, s in ((6, "D7"), (11, "D2")): gtext(s, X("H") + 0.9, Y(r), just="right", size=0.8)
NX = BW + 5
notes = ["Off-board connections (wire tails unless noted):",
         "J1  A19-D19  1x4 socket: Adafruit 4517 via 4209 cable",
         "J2  A21-D21  OLED SSD1306 (female jumper tails)",
         "J3  A22-D22  GY-MAX30102 (female jumper tails, INT open)",
         "     column A = 3V3, B = SDA, C = SCL, D = GND",
         "SW1 G22 (D2), G23 (GND)",
         "LED I22 (anode, after R1 220R), I23 (cathode, GND)",
         "",
         "F.Cu tracks: 5 insulated jumper wires, component side",
         "   3V3 B2-A18, SDA B8-B18, SCL B9-C18, D7 J6-J17, D2 J11-G21",
         "B.Cu tracks: bare wire and solder bridges, solder side",
         "   buses A/B/C rows 18-22, GND D14-D23-I23",
         "",
         "Nano ESP32 plugs into J10 (C1-C15, JP1) and J11 (I1-I15, JP2),",
         "USB-C over the row-1 edge. Row 20 is spare (test points).",
         "Buzzer not fitted. 10 x 24 hole grid assumed: count the board."]
for i, s in enumerate(notes):
    if s: gtext(s, NX, 4 + i * 2.2, just="left", size=1.1)
add(')')
open(sys.argv[1], "w").write("\n".join(out) + "\n")
print("wrote", sys.argv[1], sum(len(s) for s in out), "bytes;", len(PADNET), "pads on", len(NETS) - 1, "nets")
