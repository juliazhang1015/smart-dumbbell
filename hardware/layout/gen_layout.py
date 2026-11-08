# Smart dumbbell layout proposal v0.2: top view, longitudinal section A-A, transverse sections B-B and C-C.
# Run: python3 hardware/layout/gen_layout.py hardware/layout/layout-v0.2.svg
# Units in the geometry are millimetres; the page is pixels. Component sizes marked * in the notes are catalogue values, not measured.
import sys, math
W, H = 1800, 1400
F = "PingFang SC, Helvetica Neue, Helvetica, Arial, sans-serif"
out = []
def add(s): out.append(s)
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def tr(s): return s
def text(x, y, s, size=12, anchor="start", weight="normal", fill="#111", rot=None):
    s = tr(s)
    r = f" transform='rotate({rot} {x} {y})'" if rot is not None else ""
    add(f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}' font-weight='{weight}' fill='{fill}' font-family='{F}'{r}>{esc(s)}</text>")
def line(x1, y1, x2, y2, stroke="#111", w=1.2, dash=None):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    add(f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{stroke}' stroke-width='{w}' stroke-linecap='round'{d}/>")
def rect(x, y, w, h, fill="none", stroke="#111", sw=1.2, dash=None, rx=0):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    add(f"<rect x='{x:.1f}' y='{y:.1f}' width='{w:.1f}' height='{h:.1f}' rx='{rx}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}'{d}/>")
def poly(pts, fill="none", stroke="#111", sw=1.2, dash=None, close=True):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    tag = "polygon" if close else "polyline"
    add(f"<{tag} points='{' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}' stroke-linejoin='round'{d}/>")
def circle(cx, cy, r, fill="none", stroke="#111", sw=1.2, dash=None):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    add(f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='{r:.1f}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}'{d}/>")
def path(d, fill="none", stroke="#111", sw=1.2, dash=None):
    dd = f" stroke-dasharray='{dash}'" if dash else ""
    add(f"<path d='{d}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}'{dd}/>")

# ---- fills ----
SHELL = "url(#hShell)"; STEEL = "url(#hSteel)"; PCB = "#cfe8cf"; BANKC = "#ffd9a8"; GLASS = "#bfe3ff"; SENSOR = "#f4b6b6"; WIRE = "#8e24aa"
HID = "4 3"

# ---- dimension helpers (pixel space) ----
def arrow(x, y, ang, sz=7):
    a = math.radians(ang)
    p1 = (x - sz * math.cos(a) + sz * 0.4 * math.sin(a), y - sz * math.sin(a) - sz * 0.4 * math.cos(a))
    p2 = (x - sz * math.cos(a) - sz * 0.4 * math.sin(a), y - sz * math.sin(a) + sz * 0.4 * math.cos(a))
    poly([(x, y), p1, p2], "#111", "#111", 0.8)
def dim_h(x1, x2, y, label, ext1=None, ext2=None, size=11, above=True, c="#1a4d8f"):
    if ext1 is not None: line(x1, ext1, x1, y + (6 if ext1 < y else -6), c, 0.8)
    if ext2 is not None: line(x2, ext2, x2, y + (6 if ext2 < y else -6), c, 0.8)
    line(x1, y, x2, y, c, 0.9)
    poly([(x1, y), (x1 + 7, y - 2.8), (x1 + 7, y + 2.8)], c, c, 0.6); poly([(x2, y), (x2 - 7, y - 2.8), (x2 - 7, y + 2.8)], c, c, 0.6)
    text((x1 + x2) / 2, y - 4 if above else y + size + 2, label, size, "middle", fill=c)
def dim_v(y1, y2, x, label, ext1=None, ext2=None, size=11, left=True, c="#1a4d8f"):
    if ext1 is not None: line(ext1, y1, x + (6 if ext1 < x else -6), y1, c, 0.8)
    if ext2 is not None: line(ext2, y2, x + (6 if ext2 < x else -6), y2, c, 0.8)
    line(x, y1, x, y2, c, 0.9)
    poly([(x, y1), (x - 2.8, y1 + 7), (x + 2.8, y1 + 7)], c, c, 0.6); poly([(x, y2), (x - 2.8, y2 - 7), (x + 2.8, y2 - 7)], c, c, 0.6)
    text(x - 5 if left else x + 5, (y1 + y2) / 2 + 4, label, size, "end" if left else "start", fill=c)
def label(px, py, tx, ty, s, size=10.5, anchor="start", c="#333"):
    line(px, py, tx, ty, "#777", 0.8); circle(px, py, 1.6, "#777", "#777", 0)
    text(tx + (3 if anchor == "start" else -3), ty + 4, s, size, anchor, fill=c)

# ---- geometry (mm). Global X along the handle axis, 0 = left outer face. y up, z across. ----
HEAD, GRIP, WALL, CAP = 110.0, 140.0, 2.5, 3.0
RV, AF = 50.0, 86.603          # hex circumradius and across flats (committed v0.1 cross-section)
TOTAL = 2 * HEAD + GRIP        # 360
GOD, GID, GSTUB = 34.0, 24.0, 10.0
RHX = HEAD + GRIP              # 250: right head starts
R_IN = RV - WALL / math.cos(math.radians(30))   # inner circumradius for a uniform wall: 47.11
AF_IN = AF - 2 * WALL                             # 81.6
# right head parts (global X, y, z)
BANK = dict(x0=RHX + 12.5, L=80.0, y0=-AF_IN / 2, h=29.0, w=38.0)
HUB = dict(x0=RHX + 25.0, L=50.0, y0=-8.4, t=1.6, w=40.0)
NANO = dict(x0=RHX + 28.0, L=45.0, w=18.0, sock=8.5, t=1.6)          # sits in female headers on the hub board
IMU = dict(x0=RHX + 40.0, L=25.4, w=17.8, h=5.0, z0=11.0)
OLED = dict(x0=RHX + 58.5, L=27.0, w=28.0, t=1.6, glass=1.5, y0=36.0, win_x0=RHX + 60.0, win_L=24.0, win_w=13.0)
BTN = dict(x=RHX + 35.0, z=0.0, body=12.0, h=7.3, cap_d=6.0)
LEDP = dict(x=RHX + 47.0, z=-10.0, d=5.0)
WASH = dict(x0=8.0, n=8, t=3.0, od=50.0, idd=10.5)   # left head, on an M10 rod from the cap
SENS = dict(x=TOTAL / 2 - 5.0, L=21.0, w=15.0, t=1.6, win_L=10.0, win_w=8.0, rec_L=22.0, rec_w=16.0)



add(f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>")
add("""<defs>
<pattern id='hShell' width='6' height='6' patternUnits='userSpaceOnUse' patternTransform='rotate(45)'><rect width='6' height='6' fill='#e4e4e4'/><line x1='0' y1='0' x2='0' y2='6' stroke='#777' stroke-width='0.8'/></pattern>
<pattern id='hSteel' width='3.2' height='3.2' patternUnits='userSpaceOnUse' patternTransform='rotate(45)'><rect width='3.2' height='3.2' fill='#d6dde6'/><line x1='0' y1='0' x2='0' y2='3.2' stroke='#4a5a6a' stroke-width='0.7'/></pattern>
</defs>""")
add(f"<rect width='{W}' height='{H}' fill='white'/>")
text(24, 34, "Smart dumbbell - layout proposal v0.2 (2026-11-08): top view, section A-A, sections B-B and C-C", 20, weight="bold")
text(24, 56, "One-sided layout: power bank and all boards in the right head, steel balance washers in the left head, pulse sensor in the top of the grip. Hex section as CAD v0.1 (100 across corners, 86.6 across flats); head depth 70 -> 110 to fit the power bank. Not a print file; sizes marked * are catalogue values, measure the parts.", 11.5, fill="#444")
text(24, 74, "Lines: solid = visible edge; dashed = hidden edge; hatched = printed part cut by the section; dense hatch = steel; colour blocks = component envelopes (orange power bank, green PCB, blue display, red pulse sensor, purple wire).", 11.5, fill="#444")

# =====================================================================
# View 1: TOP VIEW (looking down; horizontal = X, vertical = z)
# =====================================================================
S = 2.5
OX, OZ = 90, 290          # pixel origin: X=0 at OX; z=0 at OZ (z positive = up on page)
def T(X, z): return (OX + S * X, OZ - S * z)
text(OX, 108, "Top view  2.5 px/mm", 13, weight="bold")
# heads: outer rectangle 110 x 100 with the top-flat edges at z = +-25 (hex side = RV/… : flat width = RV)
for hx in (0.0, RHX):
    x0, y0 = T(hx, RV); rect(x0, y0, S * HEAD, S * 2 * RV, "#f2f2f2")
    for zz in (RV / 2, -RV / 2):
        a, b = T(hx, zz); c, d = T(hx + HEAD, zz); line(a, b, c, d, "#111", 0.9)
# cap split lines
for cx in (CAP, TOTAL - CAP):
    a, b = T(cx, RV); c, d = T(cx, -RV); line(a, b, c, d, "#111", 0.9)
# grip
x0, y0 = T(HEAD, GOD / 2); rect(x0, y0, S * GRIP, S * GOD, "#e9eef3")
# sensor window on the grip (10 x 8)
x0, y0 = T(SENS["x"] - SENS["win_L"] / 2, SENS["win_w"] / 2); rect(x0, y0, S * SENS["win_L"], S * SENS["win_w"], SENSOR, "#111", 1)
x0, y0 = T(SENS["x"] - SENS["rec_L"] / 2, SENS["rec_w"] / 2); rect(x0, y0, S * SENS["rec_L"], S * SENS["rec_w"], "none", "#555", 0.8, HID)
# right head top features
x0, y0 = T(OLED["win_x0"], OLED["win_w"] / 2); rect(x0, y0, S * OLED["win_L"], S * OLED["win_w"], GLASS, "#111", 1)
x0, y0 = T(OLED["x0"], OLED["w"] / 2); rect(x0, y0, S * OLED["L"], S * OLED["w"], "none", "#2e7d32", 0.8, HID)
cx, cy = T(BTN["x"], BTN["z"]); circle(cx, cy, S * BTN["cap_d"] / 2, "#ddd", "#111", 1)
x0, y0 = T(BTN["x"] - 6, 6); rect(x0, y0, S * 12, S * 12, "none", "#555", 0.8, HID)
cx, cy = T(LEDP["x"], LEDP["z"]); circle(cx, cy, S * LEDP["d"] / 2, "#ffb3b3", "#111", 1)
# hidden internals, right head
x0, y0 = T(BANK["x0"], BANK["w"] / 2); rect(x0, y0, S * BANK["L"], S * BANK["w"], "none", "#b26a00", 0.9, HID)
x0, y0 = T(HUB["x0"], HUB["w"] / 2); rect(x0, y0, S * HUB["L"], S * HUB["w"], "none", "#2e7d32", 0.8, HID)
x0, y0 = T(NANO["x0"], NANO["w"] / 2); rect(x0, y0, S * NANO["L"], S * NANO["w"], "none", "#2e7d32", 0.8, HID)
x0, y0 = T(IMU["x0"], IMU["z0"] + IMU["w"]); rect(x0, y0, S * IMU["L"], S * IMU["w"], "none", "#2e7d32", 0.8, HID)
# hidden internals, left head: washers + rod
x0, y0 = T(WASH["x0"], WASH["od"] / 2); rect(x0, y0, S * WASH["n"] * WASH["t"], S * WASH["od"], "none", "#4a5a6a", 0.8, HID)
a, b = T(CAP, 0); c, d = T(WASH["x0"] + WASH["n"] * WASH["t"] + 8, 0); line(a, b, c, d, "#4a5a6a", 0.8, HID)
# section lines
def cut_mark(X, name, zlo=-56, zhi=70, c="#c62828"):
    a, b = T(X, zlo); d, e = T(X, zhi); line(a, b, d, e, c, 1.2, "10 4 2 4")
    for yy, ang in ((b, 0), (e, 0)):
        line(a - 14, yy, a, yy, c, 1.6); arrow(a, yy, 0, 7); text(a + 2, yy + 4, name, 11, "start", "bold", c)
cut_mark(RHX + 70, "B"); cut_mark(TOTAL / 2 - 5 + 16, "C")
# A-A: horizontal line through the axis
a, b = T(-14, 0); c, d = T(TOTAL + 8, 0); line(a, b, c, d, "#c62828", 1.2, "10 4 2 4")
for xx in (a, c):
    line(xx, b, xx, b + 16, "#c62828", 1.6); arrow(xx, b + 16, 90, 7); text(xx + 4, b + 14, "A", 11, "start", "bold", "#c62828")
# dimensions
yb = T(0, -RV)[1] + 28
dim_h(T(0, 0)[0], T(HEAD, 0)[0], yb, "110", T(0, -RV)[1], T(HEAD, -RV)[1], above=False)
dim_h(T(HEAD, 0)[0], T(RHX, 0)[0], yb, "140 (exposed grip)", T(HEAD, -GOD / 2)[1], T(RHX, -GOD / 2)[1], above=False)
dim_h(T(RHX, 0)[0], T(TOTAL, 0)[0], yb, "110", None, T(TOTAL, -RV)[1], above=False)
dim_h(T(0, 0)[0], T(TOTAL, 0)[0], yb + 30, "360 overall (CAD v0.1: 280)", above=False)
xr = T(TOTAL, 0)[0] + 56
dim_v(T(0, RV)[1], T(0, -RV)[1], xr, "100", T(TOTAL, RV)[0], T(TOTAL, -RV)[0], left=False)
dim_v(T(0, RV / 2)[1], T(0, -RV / 2)[1], xr + 40, "50 top flat", left=False)
# labels
R1, R2 = 62, 53   # two label rows above the top view (z values)
label(*T(WASH["x0"] + 12, WASH["od"] / 2 - 3), *T(15, R1), "8 steel washers on an M10 rod (hidden)", 10.5)
label(*T(SENS["x"], 0), *T(140, R2), "Pulse window 10x8 (MAX30102 below)", 10.5)
label(*T(BTN["x"], 2), *T(250, R1), "SW1 button, 6 mm cap", 10.5)
label(*T(LEDP["x"], LEDP["z"]), *T(272, R2), "LED 5 mm", 10.5)
label(*T(IMU["x0"] + 12, IMU["z0"] + 9), *T(312, R1), "4517 IMU, X along the grip", 10.5)
label(*T(OLED["win_x0"] + 12, 0), *T(305, R2), "OLED window 24x13, display below", 10.5)
label(*T(BANK["x0"] + 70, -BANK["w"] / 2 + 2), *T(380, R2), "INIU P81 power bank 80x38x29 (hidden)", 10.5)

# =====================================================================
# View 2: SECTION A-A (vertical plane through the axis; horizontal = X, vertical = y)
# =====================================================================
OY = 690
def A(X, y): return (OX + S * X, OY - S * y)
text(OX, 455, "Section A-A  through the grip axis  2.5 px/mm", 13, weight="bold")
hh = AF / 2
# shells: outer rectangle minus cavity, drawn as four hatched strips per head
def head_shell(hx, cap_at_left):
    # top and bottom walls
    for ys in (hh, -hh + WALL):
        x0, y0 = A(hx, ys); rect(x0, y0, S * HEAD, S * WALL, SHELL, "#111", 1)
    if cap_at_left:
        x0, y0 = A(hx, hh); rect(x0, y0, S * CAP, S * AF, SHELL, "#111", 1)            # cap
        x0, y0 = A(hx + HEAD - WALL, hh); rect(x0, y0, S * WALL, S * AF, SHELL, "#111", 1)  # inner wall
    else:
        x0, y0 = A(hx, hh); rect(x0, y0, S * WALL, S * AF, SHELL, "#111", 1)
        x0, y0 = A(hx + HEAD - CAP, hh); rect(x0, y0, S * CAP, S * AF, SHELL, "#111", 1)
head_shell(0.0, True); head_shell(RHX, False)
# grip openings in the inner walls (Ø34.4) : clear the wall where the grip passes
for gx in (HEAD - WALL, RHX):
    x0, y0 = A(gx, GOD / 2 + 0.2); rect(x0 - 0.5, y0, S * WALL + 1, S * (GOD + 0.4), "white", "none", 0)
# grip tube: two hatched walls from X=HEAD-GSTUB to RHX+GSTUB
for ys in (GOD / 2, -GID / 2):
    x0, y0 = A(HEAD - GSTUB, ys); rect(x0, y0, S * (GRIP + 2 * GSTUB), S * (GOD - GID) / 2, SHELL, "#111", 1)
# sensor recess + window in the grip top wall
x0, y0 = A(SENS["x"] - SENS["rec_L"] / 2, GID / 2 + 3.5); rect(x0, y0, S * SENS["rec_L"], S * 3.5, "white", "#111", 1)
x0, y0 = A(SENS["x"] - SENS["win_L"] / 2, GOD / 2); rect(x0, y0, S * SENS["win_L"], S * 1.5, "white", "#111", 1)
x0, y0 = A(SENS["x"] - SENS["L"] / 2, GID / 2 + 3.5); rect(x0, y0, S * SENS["L"], S * SENS["t"], PCB, "#2e7d32", 1)
x0, y0 = A(SENS["x"] - 2.8, GID / 2 + 3.5 + 1.4); rect(x0, y0, S * 5.6, S * 1.4, SENSOR, "#111", 0.8)
# sensor wires inside the bore to the right head, then up to the hub board
pts = [A(SENS["x"] + 8, GID / 2 + 1.9), A(SENS["x"] + 14, -6), A(RHX + GSTUB + 2, -6), A(HUB["x0"] - 2, -6)]
poly(pts, "none", WIRE, 1.4, "5 3", False)
# ---- right head contents ----
x0, y0 = A(BANK["x0"], BANK["y0"] + BANK["h"]); rect(x0, y0, S * BANK["L"], S * BANK["h"], BANKC, "#b26a00", 1)
text(x0 + S * 40, y0 + S * 16, "INIU SnapGo P81  80 x 29 (38 wide)", 10.5, "middle", fill="#7a4a00")
# bank's built-in cable: from the bank top near its cap end up to the Nano USB-C
nano_top = HUB["y0"] + HUB["t"] + NANO["sock"]
cx0, cy0 = A(BANK["x0"] + 72, BANK["y0"] + BANK["h"]); cx1, cy1 = A(NANO["x0"] + NANO["L"] + 1, nano_top + 0.8)
path(f"M{cx0:.1f},{cy0:.1f} C{cx0+30:.1f},{cy0-10:.1f} {cx1+34:.1f},{cy1-6:.1f} {cx1:.1f},{cy1:.1f}", "none", "#111", 2.2)
# hub board + ledges (ledges live on the slanted side walls; in A-A they are behind the plane: hidden)
x0, y0 = A(HUB["x0"], HUB["y0"] + HUB["t"]); rect(x0, y0, S * HUB["L"], S * HUB["t"], PCB, "#2e7d32", 1)
# Nano: sockets + board
x0, y0 = A(NANO["x0"], nano_top); rect(x0, y0, S * NANO["L"], S * NANO["sock"], "#f7f7f7", "#555", 0.8)
x0, y0 = A(NANO["x0"], nano_top + NANO["t"]); rect(x0, y0, S * NANO["L"], S * NANO["t"], PCB, "#2e7d32", 1)
x0, y0 = A(NANO["x0"] + NANO["L"] - 7, nano_top + NANO["t"] + 3.2); rect(x0, y0, S * 7, S * 3.2, "#bbb", "#333", 0.8)  # USB-C
text(A(NANO["x0"] + 22, nano_top + NANO["t"] + 8)[0], A(NANO["x0"] + 22, nano_top + NANO["t"] + 8)[1], "Nano ESP32 45x18 in female headers", 10, "middle", fill="#1b5e20")
# IMU behind the plane: visible outline
x0, y0 = A(IMU["x0"], HUB["y0"] + HUB["t"] + IMU["h"]); rect(x0, y0, S * IMU["L"], S * IMU["h"], "none", "#2e7d32", 0.9, HID)
# OLED under the top wall + window
x0, y0 = A(OLED["win_x0"], hh); rect(x0, y0, S * OLED["win_L"], S * WALL, "white", "#111", 1)
x0, y0 = A(OLED["x0"], OLED["y0"] + OLED["t"]); rect(x0, y0, S * OLED["L"], S * OLED["t"], PCB, "#2e7d32", 1)
x0, y0 = A(OLED["x0"] + 1.5, OLED["y0"] + OLED["t"] + OLED["glass"]); rect(x0, y0, S * (OLED["L"] - 3), S * OLED["glass"], GLASS, "#1565c0", 1)
for bx in (OLED["x0"] - 2.5, OLED["x0"] + OLED["L"]):   # two bosses from the top wall carrying the OLED board
    x0, y0 = A(bx, hh - WALL); rect(x0, y0, S * 2.5, S * (hh - WALL - OLED["y0"]), SHELL, "#111", 0.9)
# button: hole in the top wall, body below on a bracket
x0, y0 = A(BTN["x"] - 3.5, hh); rect(x0, y0, S * 7, S * WALL, "white", "#111", 1)
x0, y0 = A(BTN["x"] - 3, hh + 1.7); rect(x0, y0, S * 6, S * (WALL + 1.7), "#ddd", "#111", 1)      # cap
x0, y0 = A(BTN["x"] - 6, hh - WALL); rect(x0, y0, S * 12, S * BTN["h"], "#eee", "#111", 1)       # body
x0, y0 = A(BTN["x"] - 9, hh - WALL - BTN["h"]); rect(x0, y0, S * 18, S * 1.6, PCB, "#2e7d32", 1)  # small carrier board
for bx in (BTN["x"] - 11.5, BTN["x"] + 9):
    x0, y0 = A(bx, hh - WALL); rect(x0, y0, S * 2.5, S * (BTN["h"] + 1.6), SHELL, "#111", 0.9)
# LED: behind the plane (z=-10): hidden outline through the wall
x0, y0 = A(LEDP["x"] - 2.5, hh); rect(x0, y0, S * 5, S * (WALL + 6), "none", "#555", 0.8, HID)
# ---- left head contents: rod, nuts, washers ----
rod_y = 5.0
x0, y0 = A(CAP - 1, rod_y); rect(x0, y0, S * (WASH["x0"] + WASH["n"] * WASH["t"] + 8 + 1), S * 2 * rod_y, STEEL, "#333", 0.8)
for i in range(WASH["n"]):
    x0, y0 = A(WASH["x0"] + i * WASH["t"], WASH["od"] / 2); rect(x0, y0, S * WASH["t"], S * WASH["od"], STEEL, "#333", 0.8)
for nx in (CAP, WASH["x0"] + WASH["n"] * WASH["t"]):   # M10 nuts, 8 thick, 17 AF
    x0, y0 = A(nx, 8.5); rect(x0, y0, S * 8, S * 17, STEEL, "#333", 1)
x0, y0 = A(-4, 8.5); rect(x0, y0, S * 4, S * 17, STEEL, "#333", 1)   # outside nut on the cap (countersink not drawn)
text(A(52, -30)[0], A(52, -30)[1], "M10 rod + 50x3 washers, about 44 g each", 10.5, "middle", fill="#333")
text(A(52, -36)[0], A(52, -36)[1], "8 washers about 350 g; count set by balance, total <= 1 kg", 10.5, "middle", fill="#333")
# cap screws, hidden (bosses are off the plane)
for hx, sgn in ((CAP, -1), (TOTAL - CAP, 1)):
    for yy in (33, -33):
        x0, y0 = A(hx if sgn < 0 else hx - 10, yy + 1.7); rect(x0, y0, S * 10, S * 3.4, "none", "#555", 0.8, HID)
# section marks on A-A
for X, nm in ((RHX + 70, "B"), (TOTAL / 2 - 5 + 16, "C")):
    a, b = A(X, hh + 14); c, d = A(X, -hh - 14); line(a, b, c, d, "#c62828", 1.2, "10 4 2 4")
    for yy in (b, d):
        line(a - 14, yy, a, yy, "#c62828", 1.6); arrow(a, yy, 0, 7); text(a + 2, yy + 4, nm, 11, "start", "bold", "#c62828")
# dimensions on A-A
xl = A(0, 0)[0] - 30
dim_v(A(0, hh)[1], A(0, -hh)[1], xl, "86.6", A(0, hh)[0], A(0, -hh)[0], left=True)
dim_v(A(0, GOD / 2)[1], A(0, -GOD / 2)[1], A(HEAD + 45, 0)[0], "Ø34", left=True)
dim_v(A(0, GID / 2)[1], A(0, -GID / 2)[1], A(HEAD + 45, 0)[0] + 32, "Ø24", left=False)
yb2 = A(0, -hh)[1] + 26
dim_h(A(RHX + WALL, 0)[0], A(RHX + HEAD - CAP, 0)[0], yb2, "104.5 cavity", A(RHX + WALL, -hh)[1], A(RHX + HEAD - CAP, -hh)[1], above=False)
dim_h(A(BANK["x0"], 0)[0], A(BANK["x0"] + BANK["L"], 0)[0], yb2 + 26, "80 power bank", above=False)
dim_h(A(RHX, 0)[0], A(RHX + GSTUB, 0)[0], yb2 + 26, "10", above=False)
dim_h(A(BANK["x0"] + BANK["L"], 0)[0], A(RHX + HEAD - CAP, 0)[0], yb2 + 26, "14.5 cable bend", above=False)
dim_h(A(TOTAL - CAP, 0)[0], A(TOTAL, 0)[0], yb2, "3 end cap", above=False)
dim_h(A(RHX, 0)[0], A(RHX + WALL, 0)[0], A(RHX, hh)[1] - 12, "2.5 wall", above=True)
dim_h(A(OLED["win_x0"], 0)[0], A(OLED["win_x0"] + OLED["win_L"], 0)[0], A(0, hh)[1] - 14, "24", above=True)
dim_v(A(0, BANK["y0"] + BANK["h"])[1], A(0, BANK["y0"])[1], A(RHX + HEAD + 14, 0)[0], "29", A(BANK["x0"] + BANK["L"], 0)[0], A(BANK["x0"] + BANK["L"], 0)[0], left=False)
dim_v(A(0, hh)[1], A(0, OLED["y0"])[1], A(RHX + HEAD + 14, 0)[0], "7.1 display to outer face", left=False)
# labels on A-A
label(*A(SENS["x"], GID / 2 + 4.3), *A(HEAD + 4, 42), "GY-MAX30102 21x15 clipped in from the bore, chip flush", 10.5)
label(*A(SENS["x"] + 20, -6), *A(SENS["x"] + 20, -50), "4 wires run through the grip bore to the hub board (purple dashed)", 10.5)
label(*A(HUB["x0"] + 4, HUB["y0"] + 0.8), *A(RHX + HEAD + 14, -62), "Perfboard hub 50x40, female headers (half breadboard 83x55 does not fit)", 10.5)
label(*A(OLED["x0"] + 20, OLED["y0"] + 2.4), *A(OLED["x0"] + 40, 58), "OLED 0.96in 27x28 on two posts under the top wall", 10.5)
label(*A(BTN["x"], hh + 4), *A(BTN["x"] - 40, 66), "SW1 tact switch 12x12 on a small board under the top wall", 10.5, "end")
label(*A(BANK["x0"] + 76, BANK["y0"] + BANK["h"] + 6), *A(BANK["x0"] + 96, 24), "Built-in USB-C cable bends up into the Nano", 10.5)
label(*A(TOTAL - 1.5, -22), *A(TOTAL + 14, -36), "End cap: openings for the bank's charge port and button (positions from the real part)", 10.5)
label(*A(HEAD - GSTUB + 3, GOD / 2), *A(6, 52), "Grip enters the head 10 mm, 34.4 hole, radial M3 screw (not drawn)", 10.5)

# =====================================================================
# View 3: SECTION B-B (plane X = RHX+70, looking toward the cap; horizontal = z, vertical = y)
# =====================================================================
SB = 3.4
BX0, BY0 = 1500, 330
def B(z, y): return (BX0 + SB * z, BY0 - SB * y)
text(BX0 - 170, 108, "Section B-B  right head, OLED and Nano  3.4 px/mm", 13, weight="bold")
def hexpts(R, f):
    return [f(R * math.cos(math.radians(a)), R * math.sin(math.radians(a))) for a in (0, 60, 120, 180, 240, 300)]
# shell ring: outer hex minus inner hex (even-odd fill)
po = hexpts(RV, B); pi = hexpts(R_IN, B)
add(f"<path d='M{' L'.join(f'{x:.1f},{y:.1f}' for x, y in po)} Z M{' L'.join(f'{x:.1f},{y:.1f}' for x, y in pi)} Z' fill='{SHELL}' fill-rule='evenodd' stroke='#111' stroke-width='1.2'/>")
# cap-screw bosses seen behind the plane (at the cap end): circles with pilot holes
for zz, yy in ((25, 33), (-25, 33), (25, -33), (-25, -33)):
    cx, cy = B(zz, yy); circle(cx, cy, SB * 5, "#eee", "#555", 0.9); circle(cx, cy, SB * 1.3, "white", "#555", 0.8)
# bank
x0, y0 = B(-BANK["w"] / 2, BANK["y0"] + BANK["h"]); rect(x0, y0, SB * BANK["w"], SB * BANK["h"], BANKC, "#b26a00", 1)
text(B(0, BANK["y0"] + 13)[0], B(0, BANK["y0"] + 13)[1], "P81  38 x 29", 10.5, "middle", fill="#7a4a00")
# hub ledges from the slanted walls at y = HUB y0 (hatched), then the board
yl = HUB["y0"]; half_in = R_IN - abs(yl) / math.sqrt(3)
for sgn in (1, -1):
    pts = [B(sgn * half_in, yl + 1.6), B(sgn * (HUB["w"] / 2 - 1), yl + 1.6), B(sgn * (HUB["w"] / 2 - 1), yl - 2.4), B(sgn * (half_in - 2.3), yl - 2.4)]
    poly(pts, SHELL, "#111", 0.9)
x0, y0 = B(-HUB["w"] / 2, HUB["y0"] + HUB["t"]); rect(x0, y0, SB * HUB["w"], SB * HUB["t"], PCB, "#2e7d32", 1)
# Nano sockets (two rows 2.54 wide at z = +-7.6) and board
for zz in (-8.9, 6.35):
    x0, y0 = B(zz, nano_top); rect(x0, y0, SB * 2.54, SB * NANO["sock"], "#f7f7f7", "#555", 0.8)
x0, y0 = B(-NANO["w"] / 2, nano_top + NANO["t"]); rect(x0, y0, SB * NANO["w"], SB * NANO["t"], PCB, "#2e7d32", 1)
x0, y0 = B(-7, nano_top + NANO["t"] + 2.6); rect(x0, y0, SB * 14, SB * 2.6, "#cfd8dc", "#333", 0.8)   # NORA module
text(B(0, nano_top + 9)[0], B(0, nano_top + 9)[1], "Nano ESP32 (cut)", 10, "middle", fill="#1b5e20")
# bank cable crossing the plane (circle = cable cut)
cx, cy = B(26, 12); circle(cx, cy, SB * 1.8, "#333", "#111", 0.8); text(cx + 9, cy + 4, "cable", 10, fill="#333")
# OLED + glass + window in the top wall
x0, y0 = B(-OLED["win_w"] / 2, hh); rect(x0, y0, SB * OLED["win_w"], SB * WALL, "white", "#111", 1)
x0, y0 = B(-OLED["w"] / 2, OLED["y0"] + OLED["t"]); rect(x0, y0, SB * OLED["w"], SB * OLED["t"], PCB, "#2e7d32", 1)
x0, y0 = B(-OLED["w"] / 2 + 1.5, OLED["y0"] + OLED["t"] + OLED["glass"]); rect(x0, y0, SB * (OLED["w"] - 3), SB * OLED["glass"], GLASS, "#1565c0", 1)
# wires from hub to OLED (schematic)
poly([B(16, HUB["y0"] + 1.6), B(22, 10), B(22, 30), B(15, OLED["y0"])], "none", WIRE, 1.2, "5 3", False)
poly([B(-16, HUB["y0"] + 1.6), B(-24, -6), B(-34, -6), B(-34, BANK["y0"] + 8), B(-30, BANK["y0"] + 8)], "none", WIRE, 1.2, "5 3", False)
text(B(-24, -16)[0], B(-24, -16)[1], "pulse wires", 9.5, "middle", fill=WIRE)
# dims
dim_v(B(0, hh)[1], B(0, -hh)[1], B(-RV, 0)[0] - 26, "86.6", B(-RV / 2, 0)[0], B(-RV / 2, 0)[0], left=True)
dim_h(B(-RV, 0)[0], B(RV, 0)[0], B(0, -hh)[1] + 26, "100", B(-RV, 0)[1], B(RV, 0)[1], above=False)
dim_h(B(-BANK["w"] / 2, 0)[0], B(BANK["w"] / 2, 0)[0], B(0, BANK["y0"])[1] + 14, "38", above=False)
dim_v(B(0, OLED["y0"] + OLED["t"] + OLED["glass"])[1], B(0, nano_top + NANO["t"] + 2.6)[1], B(RV, 0)[0] + 24, "about 30 clearance", left=False)
dim_h(B(-OLED["w"] / 2, 0)[0], B(OLED["w"] / 2, 0)[0], B(0, hh)[1] - 14, "28", above=True)
label(*B(-half_in + 6, yl), *B(-RV - 6, -8), "Ledge on the slanted wall carries the board", 10, "end")
label(*B(-25, 33), *B(-RV - 6, 40), "End-cap bosses 10 mm, 4x M3 (behind the section)", 10, "end")

# =====================================================================
# View 4: SECTION C-C (through the grip at the sensor; horizontal = z, vertical = y)  5 px/mm
# =====================================================================
SC = 5.0
CX0, CY0 = 1540, 820
def C(z, y): return (CX0 + SC * z, CY0 - SC * y)
text(CX0 - 150, 600, "Section C-C  grip at the pulse sensor  5 px/mm", 13, weight="bold")
cx, cy = C(0, 0)
add(f"<path d='M{cx+SC*GOD/2:.1f},{cy:.1f} A{SC*GOD/2:.1f},{SC*GOD/2:.1f} 0 1 0 {cx-SC*GOD/2:.1f},{cy:.1f} A{SC*GOD/2:.1f},{SC*GOD/2:.1f} 0 1 0 {cx+SC*GOD/2:.1f},{cy:.1f} Z M{cx+SC*GID/2:.1f},{cy:.1f} A{SC*GID/2:.1f},{SC*GID/2:.1f} 0 1 0 {cx-SC*GID/2:.1f},{cy:.1f} A{SC*GID/2:.1f},{SC*GID/2:.1f} 0 1 0 {cx+SC*GID/2:.1f},{cy:.1f} Z' fill='{SHELL}' fill-rule='evenodd' stroke='#111' stroke-width='1.2'/>")
# recess from the bore side (16 wide, from r=12 up to r=15.5) and window (10 wide, through the 1.5 skin)
x0, y0 = C(-SENS["rec_w"] / 2, GID / 2 + 3.5); rect(x0, y0, SC * SENS["rec_w"], SC * 3.5 + 1, "white", "#111", 1)
x0, y0 = C(-SENS["win_w"] / 2, GOD / 2); rect(x0, y0, SC * SENS["win_w"], SC * 1.5 + 1, "white", "#111", 1)
# board, chip, header pins bent flat under the board
x0, y0 = C(-SENS["w"] / 2, GID / 2 + 3.5); rect(x0, y0, SC * SENS["w"], SC * SENS["t"], PCB, "#2e7d32", 1)
x0, y0 = C(-1.65, GID / 2 + 3.5 + 1.4); rect(x0, y0, SC * 3.3, SC * 1.4, SENSOR, "#111", 0.9)
poly([C(-5, GID / 2 + 1.9), C(-5, GID / 2 + 0.6), C(2, GID / 2 + 0.6)], "none", "#555", 1.2, None, False)
poly([C(2, GID / 2 + 0.6), C(6, -2), C(6, -10)], "none", WIRE, 1.4, "5 3", False)
# retention: two small ledges on the recess sides holding the board edges (snap lips)
for sgn in (1, -1):
    x0, y0 = C(sgn * SENS["rec_w"] / 2 - (1.5 if sgn > 0 else 0), GID / 2 + 3.5); rect(x0, y0, SC * 1.5, SC * 1.2, SHELL, "#111", 0.8)
dim_h(C(-GOD / 2, 0)[0], C(GOD / 2, 0)[0], C(0, -GOD / 2)[1] + 26, "Ø34", C(-GOD / 2, 0)[1], C(GOD / 2, 0)[1], above=False)
dim_h(C(-GID / 2, 0)[0], C(GID / 2, 0)[0], C(0, -GID / 2)[1] + 10, "Ø24", above=False)
dim_h(C(-SENS["rec_w"] / 2, 0)[0], C(SENS["rec_w"] / 2, 0)[0], C(0, GOD / 2)[1] - 30, "16 recess", above=True)
dim_h(C(-SENS["win_w"] / 2, 0)[0], C(SENS["win_w"] / 2, 0)[0], C(0, GOD / 2)[1] - 14, "8 window", above=True)
dim_v(C(0, GOD / 2)[1], C(0, GID / 2)[1], C(GOD / 2, 0)[0] + 22, "5 wall", left=False)
label(*C(0, GID / 2 + 4.2), *C(-26, 26), "MAX30102 chip 5.6x3.3, top flush with the grip surface", 10, "end")
label(*C(-5, GID / 2 + 1.2), *C(-26, 2), "Header pins bent flat and soldered, no radial space", 10, "end")
label(*C(SENS["rec_w"] / 2 - 0.7, GID / 2 + 4.1), *C(-26, -16), "Snap lips hold the board; the recess blocks light", 10, "end")

# =====================================================================
# Notes and component table
# =====================================================================
NX, NY = 90, 1000
text(NX, NY, "Component envelopes (mm)", 13, weight="bold")
rows = [("Arduino Nano ESP32", "45 x 18 x 12 (in female headers)", "official size"), ("Adafruit 4517 IMU", "25.4 × 17.8 × 5", "hardware.md; connectors not measured *"),
        ("Perfboard hub", "50 × 40 × 1.6", "proposal, not bought"), ("OLED 0.96\" SSD1306", "27 x 28 x 4, active area 22 x 11", "typical module value *"),
        ("GY-MAX30102", "21 × 15 × 3.5", "typical module value *"), ("INIU SnapGo P81", "80 x 38 x 29, 115 g", "decisions.md"),
        ("Tact switch SW1", "12 x 12 x 7.3 + cap", "kit part *"), ("Washers + M10 rod", "50 x 10.5 x 3, about 44 g each", "assumed; count per balance and the 1 kg limit")]
for i, (a, b, c) in enumerate(rows):
    y = NY + 22 + 17 * i
    text(NX, y, a, 10.5, weight="bold"); text(NX + 190, y, b, 10.5); text(NX + 420, y, c, 10.5, fill="#555")
text(NX, NY + 22 + 17 * len(rows) + 6, "* not measured; update the dictionaries at the top of the script and regenerate.", 10, fill="#777")

NX2 = 720
text(NX2, NY, "Changes from CAD v0.1, estimates, not done", 13, weight="bold")
notes = [
    "1. Head depth 70 -> 110: bank 80 along the axis + grip insertion 10 + cable bend 14.5 + wall 2.5 + cap 3. Overall 280 -> 360. Section unchanged; the 80 mm width candidate is still open.",
    "2. Buttons 3 -> 1, buzzer dropped. OLED window, button and LED all on the right head's top flat; no USB opening for the Nano in the cap, the bank's cable powers it, flashing means opening the cap.",
    "3. A half breadboard 83 x 55 x 10 fits no way into a 110 head (cavity 104.5, max inner width 94); a perfboard with female headers is the hub, Nano and 4517 plug into it.",
    "4. Mass estimate (PLA 1.24 g/cm3, 2.5 walls): two heads about 300 g, grip about 95 g, ribs about 30 g; bank 115 g, boards about 60 g; 8 washers 350 g -> about 0.95 kg.",
    "   Left head about 180 g heavier than the right. 4 washers balance the heads at about 0.8 kg total; 12 washers give 1.15 kg but 360 g off balance. No room for washers in the right head: a trade-off to decide.",
    "5. Pulse module in the top of the grip, slightly left of centre, chip flush, recess blocks light. Finger contact not yet verified (do not freeze before the AT heart-rate test); may move to the side of the grip.",
    "6. Not designed: grip-to-head fastening, bank charge port / button / display openings, cable retention, OLED and button boss sizes, print tolerances, cap sealing.",
    "7. Sources: docs/hardware.md bank cavity >= 86 x 44 x 35; docs/specification.md total mass <= 1 kg, no training ballast, balance by measured masses; HANDOFF 2026-11-06 one-sided heads, walls 2-3. The enclosure is Eric's; this drawing is an input, not a replacement.",
]
def wrap(t, n=150):
    if len(t) <= n: return [t]
    words = t.split(" "); lines = []; cur = ""
    for w in words:
        if len(cur) + len(w) + 1 > n and cur: lines.append(cur); cur = "   " + w
        else: cur = (cur + " " + w) if cur else w
    lines.append(cur); return lines
yy = NY + 22
for n in notes:
    for ln in wrap(tr(n)):
        text(NX2, yy, ln, 10.5, fill="#222"); yy += 17
add("</svg>")
open(sys.argv[1], "w").write("\n".join(out) + "\n")
print("wrote", sys.argv[1], len("\n".join(out)), "bytes")
