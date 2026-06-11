# Display Plan

Adding a physical display to EspCure lets you read chamber conditions and program status without opening a browser or the HA app. This document covers hardware options, wiring, and the ESPHome configuration skeleton.

---

## Hardware Options

### Option A — SSD1306 / SH1106 OLED (Recommended for v1)

| Spec | Value |
|---|---|
| Size | 0.96" (128×64) or 1.3" (128×64) |
| Interface | I²C (shares GPIO21/22 with SHT45 — no new wires to ESP) |
| Colors | Monochrome white, yellow, or blue |
| Voltage | 3.3 V |
| Cost | $3–6 |
| ESPHome platform | `ssd1306_i2c` (SSD1306) or `ssd1306_i2c` with `model: SH1106 128x64` |

**Pros:** Uses the existing I²C bus. SSD1306 0x3C address doesn't conflict with SHT45 0x44. Plug in, write lambda, done.

**Cons:** Monochrome, small text, limited layout.

**I2C address:** 0x3C (most common) — no address conflict with SHT45 (0x44).

---

### Option B — ST7789 1.69" TFT (Richer look)

| Spec | Value |
|---|---|
| Size | 1.69" (240×280 px) |
| Interface | SPI (needs 5 GPIOs) |
| Colors | Full color (65 K) |
| Voltage | 3.3 V |
| Cost | $5–8 |
| ESPHome platform | `ili9xxx` with `model: ST7789V` |

**Pros:** Color display, larger text, more data on screen at once.

**Cons:** Needs SPI wiring (5 additional GPIO connections).

---

### Option C — ILI9341 2.8" TFT with Touch (Future expansion)

Full-color 240×320 display with optional resistive touch. Same SPI platform (`ili9xxx`). Good for a future on-device UI but overkill for v1.

---

## Recommended: Option A (SSD1306 0.96" OLED)

Start with the OLED — it wires into the existing I²C bus and requires no new GPIO assignments. You can upgrade to a TFT later without changing other wiring.

---

## Wiring (Option A — OLED, I²C)

```
OLED VCC → ESP32-C6 3.3V
OLED GND → ESP32-C6 GND
OLED SDA → GPIO21  (same as SHT45 SDA)
OLED SCL → GPIO22  (same as SHT45 SCL)
```

That's it. Both devices share the I²C bus. No pull-up resistors needed if the SHT45 breakout board already has them (most do).

---

## Wiring (Option B — ST7789 SPI TFT)

| TFT Pin | ESP32-C6 GPIO | Notes |
|---|---|---|
| VCC | 3.3V | |
| GND | GND | |
| SCL / SCK | GPIO4 | SPI clock |
| SDA / MOSI | GPIO6 | SPI data |
| RES / RST | GPIO7 | Reset |
| DC | GPIO10 | Data/Command |
| CS | GPIO11 | Chip select |
| BL | 3.3V or GPIO | Backlight; tie to 3.3V for always-on, or use GPIO for brightness control |

> **Check GPIO availability** on your specific ESP32-C6 DevKit — GPIO12–17 are used by the SPI flash on most modules. The GPIOs listed above (4, 6, 7, 10, 11) should be safe on the Espressif ESP32-C6-DevKitC-1.

---

## ESPHome Configuration Skeleton

Add these sections to `espcure.yaml`:

### Fonts

```yaml
font:
  - file: "gfonts://Roboto"
    id: font_small
    size: 10
  - file: "gfonts://Roboto"
    id: font_medium
    size: 14
  - file: "gfonts://Roboto Bold"
    id: font_large
    size: 22
```

Or use a local BDF/TTF font file:

```yaml
font:
  - file: "fonts/opensans.ttf"
    id: font_small
    size: 10
    # Download from Google Fonts; place in a fonts/ folder next to espcure.yaml
```

---

### Display component (Option A — SSD1306 OLED)

```yaml
display:
  - platform: ssd1306_i2c
    model: "SSD1306 128x64"
    address: 0x3C
    id: oled_display
    rotation: 0°
    pages:
      - id: page_main
        lambda: |-
          // Row 1: Temperature
          it.printf(0, 0, id(font_large), "%.1f", id(chamber_temp).state);
          it.printf(84, 6, id(font_small), "C");
          it.printf(100, 0, id(font_large), "%.0f", id(chamber_rh).state);
          it.printf(120, 6, id(font_small), "%");
          // Row 2: Dew point + VPD
          it.printf(0, 32, id(font_small), "DP %.1fC", id(dew_point).state);
          it.printf(70, 32, id(font_small), "VPD %.2f", id(vpd).state);
          // Row 3: Status
          it.printf(0, 48, id(font_small), "%s", id(chamber_status).state.c_str());

      - id: page_control
        lambda: |-
          it.printf(0, 0, id(font_medium), "Target: %.1f C", id(temp_pid).target_temperature);
          it.printf(0, 20, id(font_medium), "%s", id(humidity_control_mode).state.c_str());
          it.printf(0, 40, id(font_small), "%s",
            id(frost_active) ? "FROST GUARD ACTIVE" : "Frost: OK");

      - id: page_program
        lambda: |-
          it.printf(0, 0, id(font_medium), "Programs");
          it.printf(0, 20, id(font_small), "%s", id(cure_program_status).state.c_str());
          it.printf(0, 36, id(font_small), "%s", id(cannatrol_program_status).state.c_str());
          it.printf(0, 52, id(font_small), "WiFi: %d dBm", (int)id(wifi_signal_sensor).state);
```

---

### Display component (Option B — ST7789 TFT)

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
          auto bg = Color(0x1a1a2e);    # dark navy background
          auto white = Color(0xffffff);
          auto teal = Color(0x00bcd4);
          auto yellow = Color(0xffd54f);
          auto red = Color(0xff5252);

          it.fill(bg);

          # Title
          it.printf(10, 8, id(font_large), white, "EspCure");

          # Temperature (big)
          it.printf(10, 40, id(font_large), teal, "%.1f C", id(chamber_temp).state);
          it.printf(160, 40, id(font_large), teal, "%.0f%%", id(chamber_rh).state);

          # Dew point + VPD
          it.printf(10, 100, id(font_medium), white, "Dew Pt: %.1f C", id(dew_point).state);
          it.printf(10, 120, id(font_medium), white, "VPD:    %.2f kPa", id(vpd).state);

          # Status bar
          auto status_color = id(frost_active) ? red : white;
          it.printf(10, 160, id(font_small), status_color, "%s",
            id(chamber_status).state.c_str());
          it.printf(10, 178, id(font_small), white, "%s",
            id(humidity_control_mode).state.c_str());

          # Program status
          it.printf(10, 210, id(font_small), yellow, "%s",
            id(cure_program_status).state.c_str());
          it.printf(10, 228, id(font_small), yellow, "%s",
            id(cannatrol_program_status).state.c_str());
```

---

### Optional: Page-cycle button

Add a physical momentary button to cycle display pages:

```yaml
# In GPIO assignments (use any free GPIO, e.g. GPIO9 is the BOOT button on DevKitC-1)
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO9
      mode: INPUT_PULLUP
      inverted: true
    name: "Display Page Button"
    on_click:
      then:
        - display.page.show_next: oled_display   # or tft_display
        - component.update: oled_display
```

---

### Auto page-cycle (no button needed)

If you prefer automatic cycling without a button:

```yaml
interval:
  - interval: 5s
    then:
      - display.page.show_next: oled_display
      - component.update: oled_display
```

---

## What to Show

| Page | Content |
|---|---|
| Main | Chamber temp (large) · RH (large) · Dew point · VPD |
| Control | PID target · Humidity control mode · Frost guard state |
| Programs | 18-day status · Cannatrol status · WiFi signal |

For TFT/color displays, use color coding:
- **Teal/cyan** — sensor readings
- **Yellow** — setpoints and program status
- **Red** — frost guard active, alarms
- **White** — labels
- **Dark navy background** — matches EspCure dark theme

---

## GPIO Budget After Adding OLED

| GPIO | Function |
|---|---|
| 5 | Fan SSR |
| 18 | TEC SSR |
| 19 | Heater SSR |
| 21 | I²C SDA (SHT45 + OLED) |
| 22 | I²C SCL (SHT45 + OLED) |
| 23 | Dehumidifier relay |
| **Free** | GPIO0–4, 6–8, 10–11, 20 |

The GPIO9 BOOT button on the DevKitC-1 can double as the display page-cycle button (INPUT_PULLUP, active-low).

---

## Next Steps

1. Order an SSD1306 0.96" OLED (I2C) — cheapest and simplest to validate
2. Wire it to GPIO21/22 (shared I2C bus)
3. Add the `font`, `display` blocks to `espcure.yaml`
4. Download a font file to `fonts/` or use `gfonts://` (requires internet at compile time)
5. Run `esphome config espcure.yaml` — validates display config
6. Flash and verify display shows data
7. Tune page layout, font sizes, and what data to show
