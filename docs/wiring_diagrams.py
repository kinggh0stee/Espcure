#!/usr/bin/env python3
"""Render EspCure wiring diagrams (control side + 12 V power side) to PNG."""
from PIL import Image, ImageDraw, ImageFont
import textwrap


def font(sz, bold=False):
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
        "/usr/share/fonts/truetype/liberation/LiberationSans%s.ttf" % ("-Bold" if bold else ""),
    ]:
        try:
            return ImageFont.truetype(p, sz)
        except OSError:
            continue
    return ImageFont.load_default(size=sz)


INK = (30, 33, 40)
BG = (250, 250, 252)
RED = (210, 50, 50)        # +12 V / power / heater control
BLACK = (45, 45, 48)       # GND / -12 V
BLUE = (40, 110, 215)      # SDA / TEC control
GOLD = (232, 120, 22)      # SCL (old orange)
ORANGE = (232, 120, 22)    # fan control
GREY = (120, 125, 135)

F_TITLE = font(40, True)
F_SUB = font(23)
F_BOX = font(25, True)
F_PIN = font(21)
F_SM = font(19)
F_NOTE = font(22)
F_LEGB = font(21, True)


def new(w, h):
    img = Image.new("RGB", (w, h), BG)
    return img, ImageDraw.Draw(img)


def box(d, x0, y0, x1, y1, title, fill, sub=None):
    d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=fill, outline=INK, width=3)
    d.text(((x0 + x1) / 2, y0 + 22), title, font=F_BOX, fill=INK, anchor="mm")
    if sub:
        d.text(((x0 + x1) / 2, y0 + 48), sub, font=F_SM, fill=(90, 95, 105), anchor="mm")


def pin(d, x, y, label, side, color=INK):
    r = 7
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255), outline=INK, width=2)
    if side == "right":
        d.text((x - 14, y), label, font=F_PIN, fill=color, anchor="rm")
    else:
        d.text((x + 14, y), label, font=F_PIN, fill=color, anchor="lm")


def poly(d, pts, color, w=7):
    d.line(pts, fill=color, width=w, joint="curve")


def dot(d, x, y, color):
    d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=color)


def legend(d, x, y, items):
    for lbl, c in items:
        d.line([x, y, x + 44, y], fill=c, width=8)
        d.text((x + 56, y), lbl, font=F_LEGB, fill=INK, anchor="lm")
        x += 250


def notes(d, x, y, lines, width=118):
    for n in lines:
        wrapped = textwrap.wrap(n, width=width)
        for i, line in enumerate(wrapped):
            d.text((x, y), ("•  " if i == 0 else "    ") + line, font=F_NOTE, fill=(70, 74, 82), anchor="lm")
            y += 29
        y += 5


# ════════════════════════════════════════════════════════════════════════════
# Diagram 1 — Control / low-voltage side
# ════════════════════════════════════════════════════════════════════════════
def control_diagram():
    W, H = 1680, 1160
    img, d = new(W, H)
    d.text((W / 2, 40), "EspCure — Control Wiring  (3.3 V logic side)", font=F_TITLE, fill=INK, anchor="mm")
    d.text((W / 2, 84), "ESP32-C6 GPIO → SSR control inputs  •  on-board LED & button  •  I²C sensors on a separate diagram",
           font=F_SUB, fill=(90, 95, 105), anchor="mm")

    # ESP32-C6
    EX0, EY0, EX1, EY1 = 150, 270, 560, 940
    box(d, EX0, EY0, EX1, EY1, "ESP32-C6 DevKitC-1", (224, 234, 248))
    EPX = EX1
    # Power in: the buck feeds 5 V into the USB-C port at the top of the board,
    # so it enters at the top edge rather than wrapping across the box.
    USBX = EX0 + 100
    box(d, USBX - 120, 140, USBX + 120, 215, "Buck 12 V→5 V", (245, 238, 226), "5 V via USB-C")
    poly(d, [(USBX, 215), (USBX, EY0)], RED, 9)
    d.rectangle([USBX - 22, EY0 - 7, USBX + 22, EY0 + 7], fill=(225, 228, 236), outline=INK, width=2)
    dot(d, USBX, EY0, RED)
    d.text((USBX + 34, 246), "5 V (USB-C)", font=F_PIN, fill=RED, anchor="lm")

    esp = [("GND", 410, BLACK),
           ("GPIO5", 520, ORANGE), ("GPIO18", 610, BLUE), ("GPIO19", 700, GREY),
           ("GPIO8  (WS2812 LED)", 800, GREY), ("GPIO9  (BOOT btn)", 860, GREY)]
    for lbl, y, c in esp:
        pin(d, EPX, y, lbl, "right", c)
    # on-board note for LED/button
    d.text((EX0 + 24, 800), "on-board —", font=F_SM, fill=GREY, anchor="lm")
    d.text((EX0 + 24, 860), "no wiring", font=F_SM, fill=GREY, anchor="lm")

    # SSR modules (right)
    ssr = [
        ("Fan rail SSR", "GPIO5", 250, 400, 300, 360, ORANGE),
        ("Peltier SSR (TEC)", "GPIO18", 470, 620, 520, 580, BLUE),
        ("Heater SSR (PTC)", "GPIO19", 690, 840, 740, 800, GREY),
    ]
    SPX = 1150
    risers = {"GPIO5": 900, "GPIO18": 945, "GPIO19": 990}
    gnd_taps = []
    for title, gpio, y0, y1, inp_y, inn_y, color in ssr:
        box(d, SPX, y0, SPX + 470, y1, title, (230, 232, 238), "SSR-40 DD")
        pin(d, SPX, inp_y, "IN+", "left", color)
        pin(d, SPX, inn_y, "IN−", "left", BLACK)
        # LOAD side label
        d.text((SPX + 470 - 16, (y0 + y1) / 2 + 22), "LOAD → 12 V  (power diagram)",
               font=F_SM, fill=GREY, anchor="rm")
        # control wire GPIO -> IN+
        gp_y = {"GPIO5": 520, "GPIO18": 610, "GPIO19": 700}[gpio]
        rx = risers[gpio]
        poly(d, [(EPX, gp_y), (rx, gp_y), (rx, inp_y), (SPX, inp_y)], color)
        dot(d, rx, gp_y, color)
        gnd_taps.append(inn_y)

    # GND common trunk: ESP GND -> all IN-
    gtx = 1120
    poly(d, [(EPX, 410), (gtx, 410)], BLACK)
    poly(d, [(gtx, min(gnd_taps), gtx, max(gnd_taps))] if False else [(gtx, min(gnd_taps)), (gtx, max(gnd_taps))], BLACK)
    for ty in gnd_taps:
        poly(d, [(gtx, ty), (SPX, ty)], BLACK)
        dot(d, gtx, ty, BLACK)
    dot(d, gtx, 410, BLACK)

    # I2C reminder strip
    d.text((150, 990), "I²C sensors (SHT45/SHT31 + SSD1306 OLED) share GPIO21 (SDA) / GPIO22 (SCL) — see the sensor wiring diagram (sht_wiring.png).",
           font=F_NOTE, fill=(70, 74, 82), anchor="lm")

    legend(d, 150, 1035, [("GPIO5 fan", ORANGE), ("GPIO18 TEC", BLUE), ("GPIO19 heater", GREY), ("GND common", BLACK)])
    notes(d, 150, 1075, [
        "Each GPIO drives an SSR-40 DD control input (IN+); all SSR IN− share the ESP32 GND. Outputs are active-HIGH; GPIO18/19 run LEDC at 15 Hz.",
        "3.3 V control is at the SSR-40 DD minimum (3 V) — test each SSR triggers reliably; if marginal add a 2N2222 NPN driver on the GPIO line.",
    ])
    img.save("docs/wiring_control.png")
    print("wrote docs/wiring_control.png", img.size)


# ════════════════════════════════════════════════════════════════════════════
# Diagram 2 — 12 V power side
# ════════════════════════════════════════════════════════════════════════════
def power_diagram():
    W, H = 1700, 1220
    img, d = new(W, H)
    d.text((W / 2, 40), "EspCure — Power Wiring  (12 V side)", font=F_TITLE, fill=INK, anchor="mm")
    d.text((W / 2, 84), "12 V PSU feeds the buck (ESP) and three SSR-switched loads  •  common negative return",
           font=F_SUB, fill=(90, 95, 105), anchor="mm")

    RAILX = 470          # +12 V rail (vertical, red)
    BUSY = 1000          # -12 V / GND return bus (horizontal, black)

    poly(d, [(RAILX, 230), (RAILX, 880)], RED, 8)
    poly(d, [(300, BUSY), (1360, BUSY)], BLACK, 8)
    d.text((RAILX - 12, 222), "+12 V", font=F_LEGB, fill=RED, anchor="mm")
    d.text((300, BUSY + 26), "−12 V return (common)", font=F_SM, fill=BLACK, anchor="lm")

    box(d, 110, 360, 380, 560, "12 V PSU", (224, 234, 248), "25 A switching")
    pin(d, 380, 420, "V+", "right", RED)
    pin(d, 380, 510, "V−", "right", BLACK)
    poly(d, [(380, 420), (RAILX, 420)], RED); dot(d, RAILX, 420, RED)
    poly(d, [(380, 510), (430, 510), (430, BUSY)], BLACK); dot(d, 430, BUSY, BLACK)

    box(d, 560, 210, 820, 300, "Buck 12→5 V", (245, 238, 226))
    poly(d, [(RAILX, 250), (560, 250)], RED); dot(d, RAILX, 250, RED)
    poly(d, [(560, 290), (540, 290), (540, BUSY)], BLACK); dot(d, 540, BUSY, BLACK)
    box(d, 900, 215, 1180, 295, "ESP32-C6  (VIN 5 V)", (224, 234, 248))
    poly(d, [(820, 255), (900, 255)], RED)

    ssr = [
        ("Fan rail SSR", 360, 470, 415, ORANGE),
        ("Peltier SSR (TEC)", 540, 650, 595, BLUE),
        ("Heater SSR (PTC)", 720, 830, 775, GREY),
    ]
    SX0, SX1 = 560, 880
    for title, y0, y1, my, color in ssr:
        box(d, SX0, y0, SX1, y1, title, (230, 232, 238), "SSR-40 DD")
        pin(d, SX0, my, "+ in", "left", RED)
        pin(d, SX1, my, "− out", "right", color)
        poly(d, [(RAILX, my), (SX0, my)], RED); dot(d, RAILX, my, RED)

    loads = [
        ("Fans ×3", "2× TEC hot-side + heater fan", 360, 470, 415, 450),
        ("2× Peltier TEC", "wired in parallel", 540, 650, 595, 630),
        ("PTC heater element", "12 V 50 W", 720, 830, 775, 810),
    ]
    LX0, LX1 = 980, 1360
    for (title, sub, y0, y1, py, my), (_, _, _, smy, scolor) in zip(loads, ssr):
        box(d, LX0, y0, LX1, y1, title, (226, 240, 230), sub)
        pin(d, LX0, py, "+", "left", RED)
        pin(d, LX0, my, "−", "left", BLACK)
        poly(d, [(SX1, smy), (LX0, py)], scolor)
        poly(d, [(LX0, my), (LX0 - 40, my), (LX0 - 40, BUSY)], BLACK)
        dot(d, LX0 - 40, BUSY, BLACK)

    legend(d, 110, 1055, [("+12 V rail", RED), ("switched 12 V", ORANGE), ("−12 V / GND", BLACK), ("5 V → ESP", RED)])
    notes(d, 110, 1100, [
        "SSR load terminals are stamped +/− but the SSR only switches the +12 V line: PSU +12 V → SSR + in, SSR − out → load +. The − terminal is NOT ground — each load's negative returns to the −12 V bus and never touches an SSR.",
        "All three SSR-40 DD + terminals tap the +12 V rail; the fan rail SSR powers all three fans together (it switches ON whenever a cure program is active, or the Peltier or heater is active).",
        "The 25 A PSU covers 2× TEC + heater (~4.2 A) + fans with headroom. Mount each SSR-40 DD on a heatsink when it carries > 5 A. The buck (LM2596 / MP1584EN) drops 12 V → 5 V for the ESP32 VIN.",
    ], width=128)
    img.save("docs/wiring_power.png")
    print("wrote docs/wiring_power.png", img.size)


control_diagram()
power_diagram()
