#!/usr/bin/env python3
"""Render the EspCure chamber-sensor (SHT45/SHT31) wiring diagram to PNG."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 1240
BG = (250, 250, 252)
INK = (30, 33, 40)
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)


def font(sz, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
        "/usr/share/fonts/truetype/liberation/LiberationSans%s.ttf" % ("-Bold" if bold else ""),
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, sz)
        except OSError:
            continue
    return ImageFont.load_default(size=sz)


F_TITLE = font(40, True)
F_BOX = font(26, True)
F_PIN = font(22)
F_NOTE = font(23)
F_NOTE_B = font(23, True)
F_LEG = font(22)

RED = (210, 50, 50)      # 3.3 V power
BLACK = (40, 40, 40)     # GND
GREEN = (40, 160, 70)    # SDA
YELLOW = (220, 178, 15)  # SCL


def box(x0, y0, x1, y1, title, fill):
    d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=fill, outline=INK, width=3)
    d.text(((x0 + x1) / 2, y0 + 24), title, font=F_BOX, fill=INK, anchor="mm")


def pin(x, y, label, side):
    r = 7
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255), outline=INK, width=2)
    if side == "right":   # pin on right edge of a box -> label inside-left
        d.text((x - 14, y), label, font=F_PIN, fill=INK, anchor="rm")
    else:                 # pin on left edge -> label inside-right
        d.text((x + 14, y), label, font=F_PIN, fill=INK, anchor="lm")


def wire(color, esp_xy, trunk_x, sht_y, oled_y, sht_x, oled_x):
    ex, ey = esp_xy
    w = 7
    # ESP pin -> trunk
    d.line([ex, ey, trunk_x, ey], fill=color, width=w)
    # vertical trunk (spans SHT pin .. OLED pin)
    d.line([trunk_x, sht_y, trunk_x, oled_y], fill=color, width=w)
    # trunk -> SHT  and  trunk -> OLED
    d.line([trunk_x, sht_y, sht_x, sht_y], fill=color, width=w)
    d.line([trunk_x, oled_y, oled_x, oled_y], fill=color, width=w)
    # junction dots at the three taps
    for (jx, jy) in [(trunk_x, ey), (trunk_x, sht_y), (trunk_x, oled_y)]:
        d.ellipse([jx - 6, jy - 6, jx + 6, jy + 6], fill=color)


# ── Title ──────────────────────────────────────────────────────────────────
d.text((W / 2, 40), "EspCure — Chamber Sensor (SHT45 / SHT31) Wiring",
       font=F_TITLE, fill=INK, anchor="mm")
d.text((W / 2, 84), "4-wire I²C  •  both devices powered from the ESP32-C6 on-board 3.3 V",
       font=F_NOTE, fill=(90, 95, 105), anchor="mm")

# ── Boxes ──────────────────────────────────────────────────────────────────
# ESP32-C6 (left)
EX0, EY0, EX1, EY1 = 130, 240, 560, 760
box(EX0, EY0, EX1, EY1, "ESP32-C6 DevKitC-1", (224, 234, 248))
EPX = EX1  # right edge x for pins
esp = {"3V3": 340, "GND": 440, "GPIO21 (SDA)": 560, "GPIO22 (SCL)": 660}
for lbl, y in esp.items():
    pin(EPX, y, lbl, "right")

# SHT (right-top)
SX0, SY0, SX1, SY1 = 1090, 250, 1480, 540
box(SX0, SY0, SX1, SY1, "SHT45 / SHT31   (I²C 0x44)", (224, 244, 230))
SPX = SX0  # left edge x for pins
sht = {"VIN": 320, "GND": 380, "SDA": 440, "SCL": 500}
for lbl, y in sht.items():
    pin(SPX, y, lbl, "left")

# OLED (right-bottom)
OX0, OY0, OX1, OY1 = 1090, 640, 1480, 930
box(OX0, OY0, OX1, OY1, "SSD1306 OLED   (I²C 0x3C)", (245, 238, 226))
OPX = OX0
oled = {"VCC": 700, "GND": 760, "SDA": 820, "SCL": 880}
for lbl, y in oled.items():
    pin(OPX, y, lbl, "left")

# ── Wires ──────────────────────────────────────────────────────────────────
wire(RED,   (EPX, 340), 705, 320, 700, SPX, OPX)  # 3.3 V
wire(BLACK, (EPX, 440), 745, 380, 760, SPX, OPX)  # GND
wire(GREEN, (EPX, 560), 785, 440, 820, SPX, OPX)  # SDA
wire(YELLOW, (EPX, 660), 825, 500, 880, SPX, OPX)  # SCL

# Power callout on the 3V3 pin (answers "where does it get power?")
d.text((EPX - 14, 305), "← power source", font=F_NOTE_B, fill=RED, anchor="rm")

# ── Legend + notes ─────────────────────────────────────────────────────────
LY = 980
items = [("3.3 V (power)", RED), ("GND", BLACK), ("SDA — GPIO21", GREEN), ("SCL — GPIO22", YELLOW)]
x = 150
for lbl, c in items:
    d.line([x, LY, x + 46, LY], fill=c, width=8)
    d.text((x + 58, LY), lbl, font=F_LEG, fill=INK, anchor="lm")
    x += 300

notes = [
    "Power: the ESP32-C6 DevKitC-1's on-board 3.3 V regulator feeds the SHT (VIN) and the OLED (VCC) — no separate sensor supply.",
    "Shared I²C bus: SDA=GPIO21, SCL=GPIO22. Addresses 0x44 (SHT) and 0x3C (OLED) don't conflict — wire both in parallel.",
    "Pull-ups live on the SHT breakout (Adafruit #5665 etc.) — no external resistors needed. SHT31 and SHT45 share this hookup.",
]
import textwrap
ny = 1018
for n in notes:
    for line in textwrap.wrap(n, width=108):
        d.text((150, ny), "•  " + line if line == textwrap.wrap(n, width=108)[0] else "    " + line,
               font=F_NOTE, fill=(70, 74, 82), anchor="lm")
        ny += 30
    ny += 4

img.save("docs/sht_wiring.png")
print("wrote docs/sht_wiring.png", img.size)
