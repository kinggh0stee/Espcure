# Hardware

## Bill of Materials

| # | Component | Spec / Part | Notes |
|---|---|---|---|
| 1 | **Fridge** | Honeywell thermoelectric wine cooler | Remove original control board |
| 2 | **MCU** | ESP32-C6 DevKit (e.g. Espressif ESP32-C6-DevKitC-1) | 3.3 V logic; requires ESP-IDF firmware |
| 3 | **Chamber sensor** | SHT45 breakout (Adafruit #5665 or equiv.) | I²C, 3.3 V; ±0.1 °C / ±1 % RH |
| 4 | **SSR — Fan rail** | SSR-40 DD (DC-DC solid-state relay) | Controls all 3 fans together (2 TEC hot-side + heater fan); always on |
| 5 | **SSR — TEC cooling** | SSR-40 DD | Controls both TECs in parallel; slow_pwm 20 s |
| 6 | **SSR — Heater** | SSR-40 DD | Controls PTC element only (heater fan wired to fan rail); slow_pwm 20 s |
| 7 | **PTC heater** | 12 V 50 W PTC ceramic heater with integrated 12 V fan, 87.5 × 60 × 42 mm (AliExpress) | Fan and element have **separate connectors** (white JST = fan; bare red/black = PTC element) — no splicing needed |
| 8 | **Dehumidifier** | Optional — Peltier condensation alone may suffice | If used: add AC SSR (separate part) for 120 V AC load on GPIO23 |
| 9 | **12 V PSU** | Generic 12 V 300 W switching PSU (25 A) | 25 A headroom covers 2× TECs + heater (4.2 A) + fans comfortably |
| 10 | **5 V PSU** | USB phone charger or Mean Well IRM-05-5 | Powers ESP32 only (no relay coils — SSRs draw < 20 mA from GPIO directly) |
| 11 | **OLED display** | SSD1306 0.96" 128×64 I²C OLED (e.g. AliExpress ~$3) | Shares GPIO21/22 I²C bus — no extra wiring beyond VCC/GND |
| 12 | **Misc** | 18 AWG wire, lever nuts (Wago 221), heat shrink, 3× SSR heatsinks | SSR-40 DDs must be mounted on heatsink when carrying > 5 A |

## GPIO Pinout

| GPIO | Function | Notes |
|---|---|---|
| 5 | SSR-40 DD — Fan rail IN | Active HIGH; all 3 fans; always on at boot |
| 8 | WS2812 RGB LED | Built into ESP32-C6 DevKitC-1 — no wiring needed |
| 9 | BOOT button (display page cycle) | Built into DevKitC-1 — INPUT_PULLUP, active low |
| 18 | SSR-40 DD — TEC cooling IN | slow_pwm 20 s; active HIGH; both TECs in parallel |
| 19 | SSR-40 DD — Heater IN | slow_pwm 20 s; active HIGH; PTC element only |
| 21 | SDA (SHT45 + OLED) | I²C — shared by both devices |
| 22 | SCL (SHT45 + OLED) | I²C — shared by both devices |
| 23 | Dehumidifier relay IN (optional) | Active HIGH; not part of core 3-SSR build |

> **⚠️ 3.3 V control voltage:** The ESP32-C6 GPIO outputs 3.3 V. SSR-40 DD spec says 3–32 V control, so 3.3 V is at the minimum. Test continuity of each SSR before final install — if an SSR doesn't trigger reliably, add a small NPN transistor (e.g. 2N2222) between the GPIO and SSR input to drive it at a higher current level.

## Wiring Overview

```
                     ┌──────────────────────────────────────┐
                     │        ESP32-C6 DevKitC-1            │
                     │                                      │
  SHT45 SDA ─────────┤ GPIO21 (SDA) ── OLED SDA             │
  SHT45 SCL ─────────┤ GPIO22 (SCL) ── OLED SCL             │
                     │                  GPIO5  ├──── SSR-40 DD (Fan) IN+
                     │                  GPIO8  │ WS2812 RGB LED (built-in)
                     │                  GPIO9  │ BOOT button (built-in)
                     │                  GPIO18 ├──── SSR-40 DD (TEC)  IN+
                     │                  GPIO19 ├──── SSR-40 DD (Heat) IN+
                     │                  GND    ├──── all 3 SSR IN−
                     └──────────────────────────────────────┘

  12V PSU (+) ──── SSR-40 DD (Fan)  LOAD+ ──── TEC fan 1 (+)
               │                          └──── TEC fan 2 (+)
               │                          └──── Heater fan (+)
               │
               ├──── SSR-40 DD (TEC)  LOAD+ ──── TEC 1 (+)
               │                          └──── TEC 2 (+)  [parallel]
               │
               └──── SSR-40 DD (Heat) LOAD+ ──── PTC element (+)

  12V PSU (−) ──── all TEC (−), fan (−), PTC element (−)  [common ground]

  5V USB ──────────── ESP32 VIN

  OLED VCC ─── 3.3V   OLED GND ─── GND
```

## OLED Display Wiring

The SSD1306 OLED shares the existing I²C bus — only 4 wires needed:

```
OLED VCC → ESP32 3.3V
OLED GND → ESP32 GND
OLED SDA → GPIO21  (same wire as SHT45 SDA)
OLED SCL → GPIO22  (same wire as SHT45 SCL)
```

The SSD1306 I²C address (0x3C) does not conflict with the SHT45 (0x44). No pull-up resistors are needed if the SHT45 breakout already has them (most do).

For a 1.3" SH1106 OLED, wiring is identical — change `model: "SSD1306 128x64"` to `model: "SH1106 128x64"` in `espcure.yaml`.

## Heater Wiring

The PTC heater has **two separate connectors pre-wired from the factory**:

- **White JST connector** (2 pins, thin wires) → fan. Connect to the 12 V fan rail output (fan SSR GPIO5 load side). Fan runs continuously.
- **Bare red/black wires** (thicker) → PTC ceramic element. Connect to the heater SSR output (GPIO19 load side). Element is slow-PWM controlled.

No cutting or splicing required.

## SSR-40 DD Heatsinking

The SSR-40 DDs must be mounted on aluminum heatsinks when carrying more than ~5 A. Without a heatsink they will overheat and fail. Use M3 screws and thermal paste between the SSR base and the heatsink. A single 100 × 60 mm aluminum plate works for all three SSRs if they're thermally isolated from each other.

## Mounting the SHT45

Mount the SHT45 inside the chamber, away from the Peltier cold plate and away from the dehumidifier exhaust. Ideal position: center-rear of the interior air space, elevated off the floor. The SHT45 has negligible self-heating (~0.1–0.2 °C at 3.3 V) — far less than the SHT31. Still calibrate with an offset after install. The SHT45 has an on-chip heater; in a high-humidity chamber, condensation can form on the sensor if the chamber temperature drops rapidly — use the **Clear Sensor Condensation** button in HA to pulse the heater and restore accurate readings.

## Frost Protection (Software-Only)

There is no cold-plate temperature sensor in this build. Frost protection is handled in firmware: if the chamber air temperature (SHT45) drops below the **Min Chamber Temperature** setpoint (default 4 °C / 39 °F), the PID is suspended until the chamber recovers 2 °C above that floor. Adjust the floor in HA under the **Min Chamber Temperature** number entity.

Note: without a cold-plate sensor, the protection reacts to chamber air temperature rather than the Peltier surface directly. If you observe ice forming on the Peltier fins, raise the Min Chamber Temperature setpoint.

## Original Control Board Removal

1. Unplug the fridge. Wait 30 s.
2. Remove the back panel and locate the PCB connected to the Peltier wires.
3. Disconnect the Peltier wiring harness and temperature sensor from the PCB.
4. Disconnect the fan wiring.
5. Remove the PCB entirely. Do not cut Peltier wires — desolder or use lever nuts.
6. Note Peltier polarity before disconnecting (mark wires with tape).

## Fusing

Add an automotive blade fuse holder on the 12 V positive rail:
- Peltier branch: 15 A fuse
- Heater + fan branch: 5 A fuse
- Total 12 V main: match your PSU rating (e.g. 20 A for LRS-100-12)
