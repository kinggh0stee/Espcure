# Display

The SSD1306 0.96" OLED is the implemented display option. It is live in `espcure.yaml` and wired to the existing I²C bus. This document covers the current behavior, wiring, and the upgrade path to a color TFT.

---

## Current Implementation — SSD1306 OLED

| Spec | Value |
|---|---|
| Size | 0.96" (128×64) |
| Interface | I²C (shares GPIO21/22 with SHT45 — no extra wires) |
| Colors | Monochrome |
| Voltage | 3.3 V |
| ESPHome platform | `ssd1306_i2c` |
| I²C address | 0x3C (no conflict with SHT45 at 0x44) |

---

## Wiring

```
OLED VCC → ESP32-C6 3.3V
OLED GND → ESP32-C6 GND
OLED SDA → GPIO21  (same wire as SHT45 SDA)
OLED SCL → GPIO22  (same wire as SHT45 SCL)
```

Both devices share the I²C bus. No pull-up resistors needed if the SHT45 breakout already has them (most do).

---

## 3-Page Display

The display cycles every 5 seconds automatically. Press the **BOOT button** (GPIO9, built into the DevKitC-1) to cycle pages manually.

| Page | Content |
|---|---|
| **Main** | Temperature °C (large) + RH % (large), dew point, VPD, chamber status, temp °F, frost banner |
| **Control** | Humidity control mode, temp setpoint (°C + °F), frost floor, WiFi signal |
| **Programs** | 10-Day Dry status, Cannatrol 4+4 status, active humidity/DP error |

The display auto-updates every 5 s. Page advance respects the 5 s timer — a manual press restarts it from that page.

Temperature, dew point, setpoint, frost floor, and DP-error readouts follow the **Fahrenheit Display** toggle (default OFF = °C). Turn it on to render those values in °F; the secondary readout on the main page shows the opposite unit. Toggling forces an immediate OLED refresh.

---

## Upgrading to a 1.3" SH1106 OLED

Wiring is identical. Change one line in `espcure.yaml`:

```yaml
display:
  - platform: ssd1306_i2c
    model: "SH1106 128x64"   # was "SSD1306 128x64"
```

---

## Upgrade Path — ST7789 1.69" Color TFT

For a richer UI with color coding:

| Spec | Value |
|---|---|
| Size | 1.69" (240×280 px) |
| Interface | SPI (needs 5 new GPIO connections) |
| Colors | Full color (65 K) |
| ESPHome platform | `ili9xxx` with `model: ST7789V` |

### SPI Wiring

| TFT Pin | ESP32-C6 GPIO |
|---|---|
| VCC | 3.3V |
| GND | GND |
| SCL / SCK | GPIO4 |
| SDA / MOSI | GPIO6 |
| RES / RST | GPIO7 |
| DC | GPIO10 |
| CS | GPIO11 |

> GPIO12–17 are used by the SPI flash on most ESP32-C6 modules — avoid them.
>
> **GPIO10 is shared:** the optional cold-plate DS18B20 (commented section in `espcure.yaml`) also uses GPIO10. Pick one — the TFT DC line *or* the DS18B20 — not both. If you want both, move the DS18B20 to GPIO20.

### ESPHome Config Skeleton

```yaml
spi:
  clk_pin: GPIO4
  mosi_pin: GPIO6

display:
  - platform: ili9xxx
    model: ST7789V
    cs_pin: GPIO11
    dc_pin: GPIO10
    reset_pin: GPIO7
    id: tft_display
    rotation: 90°
    pages:
      - id: page_main
        lambda: |-
          auto bg    = Color(0x1a1a2e);
          auto white = Color(0xffffff);
          auto teal  = Color(0x00bcd4);
          auto yellow = Color(0xffd54f);
          auto red   = Color(0xff5252);
          it.fill(bg);
          it.printf(10, 8,   id(font_l), white,  "EspCure");
          it.printf(10, 40,  id(font_l), teal,   "%.1f C",   id(chamber_temp).state);
          it.printf(160, 40, id(font_l), teal,   "%.0f%%",   id(chamber_rh).state);
          it.printf(10, 100, id(font_m), white,  "Dew Pt: %.1f C", id(dew_point).state);
          it.printf(10, 120, id(font_m), white,  "VPD:    %.2f kPa", id(vpd).state);
          auto sc = id(frost_active) ? red : white;
          it.printf(10, 160, id(font_s), sc,     "%s", id(chamber_status).state.c_str());
          it.printf(10, 178, id(font_s), white,  "%s", id(humidity_control_mode).state.c_str());
          it.printf(10, 210, id(font_s), yellow, "%s", id(dry10_program_status).state.c_str());
          it.printf(10, 228, id(font_s), yellow, "%s", id(cannatrol_program_status).state.c_str());
```

Color coding convention:
- **Teal** — live sensor readings
- **Yellow** — setpoints and program status
- **Red** — frost guard active, alarms
- **White** — labels and mode strings
- **Dark navy background** — matches EspCure dark theme

---

## GPIO Budget

| GPIO | Function |
|---|---|
| 5 | Fan SSR |
| 8 | WS2812 RGB LED (built-in DevKitC-1) |
| 9 | BOOT button — display page cycle (built-in DevKitC-1) |
| 18 | TEC SSR |
| 19 | Heater SSR |
| 21 | I²C SDA (SHT45 + OLED) |
| 22 | I²C SCL (SHT45 + OLED) |
| 23 | **Free** (formerly dehumidifier relay) |
| **Free** | GPIO0–4, 6–7, 10–11, 20 |

GPIO10–11 are available for the TFT DC/CS lines without reassigning anything — but note GPIO10 is the same pin the optional cold-plate DS18B20 would use, so the TFT and the DS18B20 can't both claim it (move the DS18B20 to GPIO20 if you need both).
