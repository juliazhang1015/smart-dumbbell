# Perfboard hub v1 (proposal): 30 x 70 mm board, Nano ESP32 in female headers, modules on wire tails.
# Run: python3 hardware/wiring/gen_perfboard.py hardware/wiring/perfboard-v1.svg
# Same pads and nets as kicad/gen_kicad_pcb.py: change both together.
# Net list follows schematic v1.2 and firmware/app (PIN_BTN D2, PIN_LED D7, I2C on A4/A5). Buzzer not fitted.
# Sizes marked * are catalogue values, not measured. Hole grid 10 x 24 is the usual 3x7 cm board: count before soldering.
import sys

W, H = 1960, 1400
S = 11.0                      # px per mm in the two board views
BW, BL = 30.0, 70.0           # board, mm
COLS = "ABCDEFGHIJ"
X0, Y0, P = 3.57, 5.79, 2.54  # first hole and pitch, mm
def X(c): return X0 + P * COLS.index(c)
def Y(r): return Y0 + P * (r - 1)

RED, BLK, BLU, YEL, GRN, ORG = "#d32f2f", "#1d1d1d", "#1565c0", "#e0a800", "#2a9d3a", "#ef6c00"
F = "PingFang SC, Helvetica Neue, Helvetica, Arial, sans-serif"
out = []
def add(s): out.append(s)
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def text(x, y, s, size=12, anchor="start", weight="normal", fill="#222", halo=None, rot=None):
    h = f" paint-order='stroke' stroke='{halo}' stroke-width='3' stroke-linejoin='round'" if halo else ""
    r = f" transform='rotate({rot} {x:.1f} {y:.1f})'" if rot is not None else ""
    add(f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}' font-weight='{weight}' fill='{fill}'{h}{r}>{esc(s)}</text>")
def rect(x, y, w, h, fill="none", stroke="#333", sw=1.2, rx=0, dash=None, op=None):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    o = f" fill-opacity='{op}'" if op is not None else ""
    add(f"<rect x='{x:.1f}' y='{y:.1f}' width='{w:.1f}' height='{h:.1f}' rx='{rx}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}'{d}{o}/>")
def circle(x, y, r, fill, stroke="none", sw=1):
    add(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r:.1f}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}'/>")
def line(x1, y1, x2, y2, stroke="#333", sw=1.2, dash=None):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    add(f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{stroke}' stroke-width='{sw}' stroke-linecap='round'{d}/>")
def wire(pts, color, w=9.0, casing="#ffffff"):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    add(f"<polyline points='{d}' fill='none' stroke='{casing}' stroke-width='{w + 2.4}' stroke-linecap='round' stroke-linejoin='round'/>")
    add(f"<polyline points='{d}' fill='none' stroke='{color}' stroke-width='{w}' stroke-linecap='round' stroke-linejoin='round'/>")
def curve(p0, p1, p2, p3, color, w=5.0):
    d = f"M{p0[0]:.1f},{p0[1]:.1f} C{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}"
    add(f"<path d='{d}' fill='none' stroke='#ffffff' stroke-width='{w + 2}' stroke-linecap='round'/>")
    add(f"<path d='{d}' fill='none' stroke='{color}' stroke-width='{w}' stroke-linecap='round'/>")
def callout(px, py, tx, ty, s, size=12, anchor="start", fill="#222"):
    line(px, py, tx, ty, "#666", 0.9); circle(px, py, 2.2, "#666")
    text(tx + (4 if anchor == "start" else -4), ty + 4, s, size, anchor, fill=fill)

LEFT = ["D13", "3V3", "B0", "A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "VBUS", "B1", "GND", "VIN"]     # JP1, pin 1 at the USB end
RIGHT = ["D12", "D11", "D10", "D9", "D8", "D7", "D6", "D5", "D4", "D3", "D2", "GND", "RST", "RX0", "TX1"]   # JP2
USED_L = {"3V3": RED, "A4": BLU, "A5": YEL, "GND": BLK}
USED_R = {"D7": ORG, "D2": GRN}
NX0, NX1 = 16.27 - 9.0, 16.27 + 9.0            # Nano 18 mm wide, centred between columns C and I
NY0, NY1 = Y(1) - 4.72, Y(15) + 4.72           # 45 mm long *, assumed symmetric about the pin rows

add(f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}' font-family='{F}'>")
add(f"<rect width='{W}' height='{H}' fill='#ffffff'/>")
text(30, 40, "Smart dumbbell - 洞洞板集线板 v1（提案，2026-11-16）", 22, weight="bold")
text(30, 64, "板：套件里的 30 × 70 mm 双面洞洞板（标准 10 × 24 孔，焊前数一下）。Nano 插排母不焊死；OLED、MAX30102 用母头杜邦线尾巴引出去；4517 用 4209 线插 1×4 排母；SW1、LED 用导线引到外壳顶面。", 12.5, fill="#444")
text(30, 83, "网表按原理图 v1.2 和 firmware/app：I2C = A4/A5，SW1 = D2，LED = D7 经 R1 220 Ω，蜂鸣器不装。孔位写法：列字母 A–J + 行号 1–24，例如 B8。带 * 的尺寸是目录值，没量实物。", 12.5, fill="#444")

# ------------------------------------------------------------------ board drawing shared by both views
def board(ox, oy, mirror, title):
    def T(x, y): return (ox + S * ((BW - x) if mirror else x), oy + S * y)
    text(ox, oy - 52, title, 14, weight="bold")
    rect(ox, oy, S * BW, S * BL, "#2f7d4f", "#184a2c", 1.5, rx=6)
    for cx, cy in ((2.3, 2.3), (BW - 2.3, 2.3), (2.3, BL - 2.3), (BW - 2.3, BL - 2.3)):
        px, py = T(cx, cy); circle(px, py, S * 1.0, "#ffffff", "#184a2c", 1)
    for c in COLS:
        for r in range(1, 25):
            px, py = T(X(c), Y(r)); circle(px, py, S * 0.95, "#dcd9c6"); circle(px, py, S * 0.42, "#1c3a2b")
    for c in COLS:
        px, py = T(X(c), 0); text(px, py - 24, c, 12.5, "middle", "bold", "#333")
    return T

def rownums(T, xmm, dx, anchor, rows, skip=()):
    for r in rows:
        if r in skip: continue
        px, py = T(xmm, Y(r)); text(px + dx, py + 4, str(r), 10.5, anchor, fill="#555")

# =================================================================== VIEW 1: component side
TX, TY = 330, 190
T = board(TX, TY, False, "① 正面（元件面）俯视  11 px/mm")
rownums(T, BW, 10, "start", range(1, 25), (3, 9, 13, 16, 20)); rownums(T, 0, -10, "end", range(1, 18))

# female headers for the Nano, columns C and I, rows 1-15
for c in ("C", "I"):
    px, py = T(X(c) - 1.27, Y(1) - 1.27); rect(px, py, S * 2.54, S * (14 * P + 2.54), "#1b1b1b", "#000", 1, rx=2)
    for r in range(1, 16):
        qx, qy = T(X(c), Y(r)); rect(qx - 3.6, qy - 3.6, 7.2, 7.2, "#6d6d6d", "#000", 0.6)

# R1 on column J, rows 18-22
ax, ay = T(X("J"), Y(18)); bx, by = T(X("J"), Y(22))
line(ax, ay, bx, by, "#b9b9b9", 3)
rect(ax - S * 1.15, (ay + by) / 2 - S * 3.15, S * 2.3, S * 6.3, "#e7cf9a", "#7a6a3a", 1, rx=5)
for i, col in enumerate(("#c62828", "#c62828", "#6d4c41", "#c9a227")):
    rect(ax - S * 1.15, (ay + by) / 2 - S * 2.3 + i * S * 1.25, S * 2.3, S * 0.55, col, "none", 0)
circle(ax, ay, 4.2, "#c9c9c9", "#555", 0.8); circle(bx, by, 4.2, "#c9c9c9", "#555", 0.8)

# feeder wires on the component side (insulated), mm coordinates
def feeder(pts, color):
    wire([T(x, y) for x, y in pts], color, 9.0)
    for x, y in (pts[0], pts[-1]):
        px, py = T(x, y); circle(px, py, 5.2, color, "#ffffff", 1.4)
feeder([(X("B"), Y(2)), (1.5, Y(2) + 2.0), (1.5, Y(17) - 1.0), (X("A"), Y(18))], RED)
feeder([(X("B"), Y(8)), (3.0, Y(8) + 1.9), (3.0, Y(17) - 0.6), (X("B"), Y(18))], BLU)
feeder([(X("B"), Y(9)), (4.55, Y(9) + 1.6), (4.55, Y(16) + 0.2), (X("C"), Y(18))], YEL)
feeder([(X("J"), Y(6)), (28.4, Y(6) + 1.6), (28.4, Y(16) + 0.9), (X("J"), Y(17))], ORG)
feeder([(X("J"), Y(11)), (X("J"), Y(16) - 0.5), (X("G") + 0.6, Y(16) - 0.5), (X("G"), Y(16) + 0.6), (X("G"), Y(21))], GRN)

# module boxes on the left and their tails
def modbox(x, y, w, h, title, sub, pins, fill):
    rect(x, y, w, h, fill, "#223", 1.2, rx=8)
    text(x + 12, y + 22, title, 13.5, weight="bold", fill="#fff"); text(x + 12, y + 39, sub, 10.5, fill="#e3e6f0")
    pos = {}
    for i, (name, col) in enumerate(pins):
        yy = y + h - 14 - (len(pins) - 1 - i) * 17
        text(x + w - 16, yy + 4, name, 11, "end", "bold", "#fff")
        circle(x + w - 8, yy, 4.2, col if col else "#aaa", "#fff", 1)
        pos[name] = (x + w - 8, yy)
    return pos
def tail(c, r, target, color, k):
    p = T(X(c), Y(r))
    curve(p, (p[0] - 70, p[1] + (k - 1.5) * 9), (target[0] + 70, target[1]), target, color, 4.6)
def enddot(c, r, color):
    px, py = T(X(c), Y(r)); circle(px, py, 5.2, color, "#ffffff", 1.4)

imu = modbox(28, 640, 214, 122, "Adafruit 4517 (IMU)", "QT 口插 4209 线，杜邦针插 J1", [("V+ 红", RED), ("GND 黑", BLK), ("SDA 蓝", BLU), ("SCL 黄", YEL)], "#4a2d8a")
oled = modbox(28, 792, 214, 122, "OLED SSD1306", "丝印顺序 GND-VCC-SCL-SDA", [("GND 黑", BLK), ("VCC 红", RED), ("SCL 黄", YEL), ("SDA 蓝", BLU)], "#2b4a7a")
mx = modbox(28, 944, 214, 138, "GY-MAX30102", "在握把里，线走握把内孔", [("VIN 红", RED), ("GND 黑", BLK), ("SCL 黄", YEL), ("SDA 蓝", BLU), ("INT 不接", None)], "#5a3a8a")
NETCOL = {"A": RED, "B": BLU, "C": YEL, "D": BLK}
for row, pos, names in ((19, imu, {"A": "V+ 红", "B": "SDA 蓝", "C": "SCL 黄", "D": "GND 黑"}),
                        (21, oled, {"A": "VCC 红", "B": "SDA 蓝", "C": "SCL 黄", "D": "GND 黑"}),
                        (22, mx, {"A": "VIN 红", "B": "SDA 蓝", "C": "SCL 黄", "D": "GND 黑"})):
    for k, c in enumerate("DCBA"):
        tail(c, row, pos[names[c]], NETCOL[c], k)
# J1: 1x4 female header on row 19 with the four 4209 pins plugged in
px, py = T(X("A") - 1.27, Y(19) - 1.27); rect(px, py, S * (3 * P + 2.54), S * 2.54, "#1b1b1b", "#000", 1, rx=2)
for c, col in zip("ABCD", (RED, BLU, YEL, BLK)):
    qx, qy = T(X(c), Y(19)); rect(qx - S * 1.05, qy - S * 1.05, S * 2.1, S * 2.1, "#2b2b2b", "#777", 0.8, rx=2); circle(qx, qy, 4.6, col, "#fff", 1.2)
for row in (21, 22):
    for c in "ABCD": enddot(c, row, NETCOL[c])

# SW1 and LED below the board
def below(c, r, tx, ty, color, bend):
    p = T(X(c), Y(r)); curve(p, (p[0] + bend, p[1] + 60), (tx, ty - 60), (tx, ty), color, 4.6)
SWX, LEDX, BY2 = 470, 660, 1050
rect(SWX - 62, BY2, 124, 74, "#333", "#111", 1.2, rx=8); circle(SWX, BY2 + 30, 15, "#2a9d3a", "#111", 1.2)
text(SWX, BY2 + 64, "SW1 轻触开关", 11.5, "middle", "bold", "#fff")
rect(LEDX - 62, BY2, 124, 74, "#fff5f5", "#900", 1.2, rx=8); circle(LEDX, BY2 + 30, 14, "#e53935", "#900", 1.2)
text(LEDX, BY2 + 64, "LED 红或黄", 11.5, "middle", "bold", "#900")
below("G", 22, SWX - 22, BY2, GRN, -30); below("G", 23, SWX + 22, BY2, BLK, 6)
below("I", 22, LEDX - 22, BY2, ORG, 14); below("I", 23, LEDX + 22, BY2, BLK, 40)
enddot("G", 22, GRN); enddot("G", 23, BLK); enddot("I", 22, ORG); enddot("I", 23, BLK)
text(SWX, BY2 + 92, "两脚：G22（D2）、G23（GND）", 11, "middle")
text(LEDX, BY2 + 92, "长脚 I22，短脚 I23（GND）", 11, "middle")
text((SWX + LEDX) / 2, BY2 + 112, "两端都是焊的；想做成可拆就在外壳那头加 2P 排针 + 母头线", 11, "middle", fill="#555")

# Nano outline on top (translucent), pin names, USB-C
px, py = T(NX0, NY0); rect(px, py, S * (NX1 - NX0), S * (NY1 - NY0), "#00a39b", "#005f5a", 1.6, rx=6, dash="7 4", op=0.20)
ux, uy = T(16.27 - 4.5, -1.6); rect(ux, uy, S * 9.0, S * 7.4, "#cfcfcf", "#555", 1.2, rx=4)
text(T(16.27, 0)[0], T(0, 2.9)[1], "USB-C", 11, "middle", "bold", "#333")
for i, n in enumerate(LEFT):
    qx, qy = T(X("C") + 1.9, Y(i + 1)); col = USED_L.get(n)
    text(qx, qy + 4, n, 10.5 if not col else 12, "start", "bold" if col else "normal", "#ffffff", halo=(col if col else "#1f5d43"))
for i, n in enumerate(RIGHT):
    qx, qy = T(X("I") - 1.9, Y(i + 1)); col = USED_R.get(n)
    text(qx, qy + 4, n, 10.5 if not col else 12, "end", "bold" if col else "normal", "#ffffff", halo=(col if col else "#1f5d43"))
cx, cy = T(16.27, Y(8))
text(cx + 5, cy, "Nano ESP32  ·  插在排母上，不焊，可拔", 13.5, "middle", "bold", "#ffffff", halo="#1f5d43", rot=-90)

# callouts, view 1
RX = TX + S * BW + 40
callout(*T(16.27 + 4.5, 1.0), RX, TY - 8, "USB-C 这端伸出板外，对着端盖 / 充电宝线")
callout(*T(X("I") + 1.2, Y(3)), RX, T(0, Y(3))[1], "排母 1×15 两条：C 列、I 列，第 1–15 行")
callout(*T(28.4, Y(9)), RX, T(0, Y(9))[1], "橙线 D7：J6 → J17")
callout(*T(X("J"), Y(13)), RX, T(0, Y(13))[1], "绿线 D2：J11 → G21（从 Nano 尾巴下面过）")
callout(*T(X("D"), Y(16)), RX, T(0, Y(16))[1], "GND 在背面：D14–D23 裸线，和 C14 脚焊在一起")
callout(*T(X("J") + 1.2, Y(20)), RX, T(0, Y(20))[1], "R1 220 Ω：J18–J22 平躺")
text(28, 214, "正面五根飞线（绝缘线）", 13, weight="bold")
for i, (col, name, hop) in enumerate(((RED, "3V3", "B2 → A18"), (BLU, "SDA (A4)", "B8 → B18"), (YEL, "SCL (A5)", "B9 → C18"), (ORG, "D7 (LED)", "J6 → J17"), (GRN, "D2 (SW1)", "J11 → G21"), (BLK, "GND", "不用飞线：背面 D 列裸线"))):
    yy = 238 + i * 21
    line(30, yy - 4, 62, yy - 4, col, 6); text(74, yy, name, 12, weight="bold"); text(160, yy, hop, 12)
for i, t_ in enumerate(("线头不进针脚那个孔，进旁边的孔（B 列 / J 列），",
                        "在背面掰向针脚焊在一起（见 ②）。",
                        "",
                        "J2、J3：母头杜邦线剪掉一端，剥线穿孔焊在板上，",
                        "母头套模块的针。列序固定：A 红 3V3、B 蓝 SDA、",
                        "C 黄 SCL、D 黑 GND，按线色对模块丝印。",
                        "",
                        "第 20 行空着：留下烙铁的位置，也是四条总线的",
                        "测试点。E、F 列和第 24 行没用，可以穿扎带绑线。")):
    text(28, 384 + i * 17, t_, 11.5, fill="#444")
text(28, 632, "J1（第 19 行排母）→ 4517", 12, weight="bold"); text(28, 784, "J2（第 21 行，焊线）→ OLED", 12, weight="bold"); text(28, 936, "J3（第 22 行，焊线）→ MAX30102", 12, weight="bold")

# =================================================================== VIEW 2: solder side (mirrored)
BX, BYv = 1030, 190
B = board(BX, BYv, True, "② 背面（焊接面）：板子左右翻过来看，列序变成 J → A")
rownums(B, 0, 10, "start", range(1, 25), (2, 8, 9, 14, 23))
for c in ("C", "I"):
    for r in range(1, 16):
        px, py = B(X(c), Y(r)); circle(px, py, S * 0.80, "#c4c8cc", "#6d7378", 0.8)
def trace(pads, color, w=7.0):
    pts = [B(X(c), Y(r)) for c, r in pads]
    wire(pts, color, w, "#f4f4f4")
    for p in pts: circle(p[0], p[1], 5.6, "#e9edf0", color, 2.0)
SIL = "#8a9299"
trace([("A", 18), ("A", 22)], RED); trace([("B", 18), ("B", 22)], BLU); trace([("C", 18), ("C", 22)], YEL)
trace([("D", 14), ("D", 23), ("I", 23)], BLK)
for a, b, col in ((("B", 2), ("C", 2), RED), (("B", 8), ("C", 8), BLU), (("B", 9), ("C", 9), YEL), (("C", 14), ("D", 14), BLK),
                  (("J", 6), ("I", 6), ORG), (("J", 11), ("I", 11), GRN), (("J", 17), ("J", 18), ORG), (("J", 22), ("I", 22), ORG), (("G", 21), ("G", 22), GRN)):
    trace([a, b], col)
for c, r in [(c, r) for r in (19, 21, 22) for c in "ABCD"] + [("G", 23), ("I", 23), ("A", 20), ("B", 20), ("C", 20), ("D", 20)]:
    px, py = B(X(c), Y(r)); circle(px, py, 5.6, "#e9edf0", NETCOL.get(c, BLK), 2.0)
# labels, view 2
LB = BX - 26; RB = BX + S * BW + 40
def pinlab(c, r, s, col, side):
    px, py = B(X(c), Y(r))
    if side == "r": line(px + 8, py, RB - 4, py, col, 0.9, "3 3"); text(RB, py + 4, s, 12, "start", "bold", col)
    else: line(px - 8, py, LB + 4, py, col, 0.9, "3 3"); text(LB, py + 4, s, 12, "end", "bold", col)
pinlab("B", 2, "3V3  C2 + B2", RED, "r"); pinlab("B", 8, "SDA  C8 + B8", BLU, "r"); pinlab("B", 9, "SCL  C9 + B9", "#a67c00", "r")
pinlab("D", 14, "GND  C14 + D14", BLK, "r"); pinlab("D", 23, "GND 轨", BLK, "r")
pinlab("J", 6, "D7  I6 + J6", ORG, "l"); pinlab("J", 11, "D2  I11 + J11", "#1b7a2a", "l")
pinlab("J", 17, "J17 线头 + J18 R1", ORG, "l"); pinlab("J", 22, "J22 R1 + I22 LED+", ORG, "l")
# do-not-bridge marks
def nobridge(c1, r1, c2, r2):
    a = B(X(c1), Y(r1)); b = B(X(c2), Y(r2)); mx_, my_ = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    line(mx_ - 5, my_ - 5, mx_ + 5, my_ + 5, "#ffeb3b", 2.6); line(mx_ - 5, my_ + 5, mx_ + 5, my_ - 5, "#ffeb3b", 2.6)
for a in ((("B", 8), ("B", 9)), (("J", 11), ("J", 12)), (("I", 11), ("I", 12)), (("I", 22), ("I", 23)), (("G", 22), ("G", 23)),
          (("A", 18), ("B", 18)), (("B", 18), ("C", 18)), (("C", 18), ("D", 18)), (("C", 2), ("C", 3)), (("C", 14), ("C", 15)), (("C", 14), ("C", 13)), (("D", 15), ("C", 15)), (("D", 13), ("D", 14))):
    nobridge(a[0][0], a[0][1], a[1][0], a[1][1])
for i, (t_, bold) in enumerate((("竖总线（第 18–22 行）：A 3V3、B SDA、C SCL；D 列是 GND，", True),
                                ("一根裸线从 D14 到 D23 再横到 I23。都用电阻脚压在焊盘上焊。", True),
                                ("绿色小桥 G21（线头）+ G22（SW1）；G23、I23 落在 GND 轨上。", False),
                                ("黄色 × = 相邻但不同网络，最容易连锡：B8/B9（SDA/SCL）、", False),
                                ("D2 旁边的 GND、C14 / D15 旁边的 B1 和 VIN、总线之间。", False),
                                ("银色圆点 = 排母的 30 个焊点，只有 6 个脚接线，其余只起固定。", False))):
    text(BX - 20, BYv + S * BL + 26 + i * 18, t_, 12, weight="bold" if bold else "normal", fill="#222" if bold else "#555")

# =================================================================== VIEW 3: side elevation
SX, SY, SS = 960, 1320, 7.0     # board top surface at SY
def E(xmm, zmm): return (SX + SS * xmm, SY - SS * zmm)
text(SX - 150, 1128, "③ 侧视（沿长边看）  7 px/mm：高度是给外壳用的", 14, weight="bold")
x0, y0 = E(0, 0); rect(x0, y0, SS * BL, SS * 1.6, "#2f7d4f", "#184a2c", 1)
x0, y0 = E(Y(1) - 1.27, 8.5); rect(x0, y0, SS * 38.1, SS * 8.5, "#2b2b2b", "#000", 1)
x0, y0 = E(Y(1) - 1.27, 11.0); rect(x0, y0, SS * 38.1, SS * 2.5, "#444", "#000", 0.8)
x0, y0 = E(NY0, 12.6); rect(x0, y0, SS * (NY1 - NY0), SS * 1.6, "#00857f", "#005f5a", 1)
x0, y0 = E(NY0 - 1.6, 15.8); rect(x0, y0, SS * 7.4, SS * 3.2, "#cfcfcf", "#555", 1)
x0, y0 = E(NY0 + 12, 15.4); rect(x0, y0, SS * 16, SS * 2.8, "#b8c2c8", "#555", 1)
x0, y0 = E(-22, 17.2); rect(x0, y0, SS * 20.4, SS * 6.0, "none", "#555", 1, rx=4, dash="5 3")
text(E(-12, 0)[0], E(0, 18.6)[1], "充电宝线插头", 11, "middle", fill="#555")
x0, y0 = E(Y(19) - 1.27, 8.5); rect(x0, y0, SS * 2.54, SS * 8.5, "#2b2b2b", "#000", 1)
x0, y0 = E(Y(19) - 1.27, 22.5); rect(x0, y0, SS * 2.54, SS * 14.0, "#555", "#000", 1)
x0, y0 = E(Y(18), 2.3); rect(x0, y0, SS * (4 * P), SS * 2.3, "#e7cf9a", "#7a6a3a", 1, rx=4)
for r in (21, 22):
    a = E(Y(r), 0); add(f"<path d='M{a[0]:.1f},{a[1]:.1f} q0,-14 30,-16' fill='none' stroke='#777' stroke-width='2.2'/>")
x0, y0 = E(2, -1.6); rect(x0, y0 , SS * 66, SS * 2.0, "none", "#999", 0.9, dash="3 3")
def dimv(xmm, z1, z2, s, side=1):
    a = E(xmm, z1); b = E(xmm, z2); line(a[0], a[1], b[0], b[1], "#1a4d8f", 1)
    for p in (a, b): line(p[0] - 5, p[1], p[0] + 5, p[1], "#1a4d8f", 1)
    text(a[0] + 7 * side, (a[1] + b[1]) / 2 + 4, s, 11.5, "start" if side > 0 else "end", fill="#1a4d8f")
dimv(74, 0, 22.5, "J1 + 4209 插头 ≈ 22.5 *（全板最高）")
dimv(67.0, 0, 15.8, "Nano 顶 ≈ 16 *", -1)
dimv(74, -3.6, 0, "板厚 1.6 + 焊点 ≈ 2")
text(E(20, 0)[0], E(0, 5.0)[1], "排母 8.5 *", 11, "middle", fill="#ffffff")
text(E(20, 0)[0], E(0, -6.3)[1], "底面留 ≥ 2 mm，垫一层绝缘（美纹纸 / 泡棉胶）再靠近充电宝", 11.5, "middle", fill="#555")

# =================================================================== tables on the right
PX = 1510
def block(y, title, rows, size=12, lh=18.5):
    text(PX, y, title, 14, weight="bold"); y += 8
    for r in rows:
        y += lh
        if isinstance(r, tuple): text(PX, y, r[0], size, weight="bold", fill=r[2] if len(r) > 2 else "#222"); text(PX + 102, y, r[1], size)
        else: text(PX, y, r, size)
    return y + 30
y = 150
y = block(y, "用料", [
    ("洞洞板", "30 × 70 mm × 1（套件有 5 片）"),
    ("排母", "1×15 × 2 + 1×4 × 1：一条 40P 够剪，"),
    ("", "每剪一刀废 1 孔（剪在第 16、32、37 孔）"),
    ("R1", "220 Ω × 1"),
    ("LED / SW1", "课程套件：红或黄 LED × 1，轻触开关 × 1"),
    ("母头杜邦线", "8 根：OLED 4 根约 10 cm，MAX30102 4 根"),
    ("", "按握把量长度（约 20 cm *），剪掉一端剥线"),
    ("飞线", "5 根绝缘线（单芯 0.5 mm 最好焊），正面走"),
    ("裸铜线", "剪下来的电阻脚：背面 3 条总线 + GND 长线"),
    ("其他", "SW1、LED 各 2 根线；热熔胶；热缩管或胶布"),
    ("不用", "KF301 端子（5.08 间距、高约 10 mm）、排针、"),
    ("", "其余尺寸的板"),
])
y = block(y, "孔位表", [
    ("排母", "C1–C15、I1–I15；J1：A19–D19"),
    ("飞线（正面）", "红 B2→A18   蓝 B8→B18   黄 B9→C18"),
    ("", "橙 J6→J17   绿 J11→G21（GND 不用飞线）"),
    ("针脚桥（背面）", "B2-C2  B8-C8  B9-C9  C14-D14  J6-I6  J11-I11"),
    ("总线（背面）", "A18–A22  B18–B22  C18–C22  D14–D23–I23"),
    ("小桥（背面）", "J17-J18   J22-I22   G21-G22"),
    ("R1", "J18、J22"),
    ("J2 OLED", "A21 红 VCC  B21 蓝 SDA  C21 黄 SCL  D21 黑 GND"),
    ("J3 MAX", "A22 红 VIN  B22 蓝 SDA  C22 黄 SCL  D22 黑 GND"),
    ("SW1 / LED", "G22、G23 / I22（长脚）、I23"),
])
y = block(y, "焊接顺序", [
    "1. 两条 1×15 排母先套在 Nano 的针上，再一起插进 C、I 列，",
    "    用 Nano 当夹具保证垂直；先焊四个角，再焊满，然后拔下 Nano。",
    "2. 焊 J1 排母和 R1。",
    "3. 背面：三条竖总线、D 列 GND 长线（D14–D23–I23）、三个小桥。",
    "4. 正面五根飞线：线头从旁边那个孔穿到背面，掰向针脚焊在一起。",
    "5. OLED、MAX30102 的尾线，SW1、LED 的线；线根点热熔胶。",
    "6. 不插 Nano 先用万用表查（下面），再上电跑 bus_check。",
])
y = block(y, "上电前用万用表查（不插 Nano、不接模块）", [
    "不通：C2↔C14（3V3↔GND）、C8↔C9（SDA↔SCL）、",
    "          C8/C9 各自对 C2 和 C14、I11↔I12（D2↔GND，按下 SW1 才通）",
    "通：C2↔A19/A21/A22，C8↔B 列，C9↔C 列，C14↔D 列和 G23、I23，",
    "       I11↔G22，I6↔J17（I6↔I22 应约 220 Ω）",
    "上电后：SDA、SCL 空闲电平应 ≥ 2.5 V（README 里一直没量的那项）",
])
add("</svg>")
open(sys.argv[1], "w").write("\n".join(out) + "\n")
print("wrote", sys.argv[1], sum(len(s) for s in out), "bytes")
