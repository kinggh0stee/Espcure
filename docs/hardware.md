# Hardware

## Bill of Materials

| # | Component | Spec / Part | Notes |
|---|---|---|---|
| 1 | **Fridge** | Honeywell thermoelectric wine cooler | Remove original control board |
| 2 | **MCU** | ESP32-C6 DevKit (e.g. Espressif ESP32-C6-DevKitC-1) | 3.3 V logic; requires ESP-IDF firmware |
| 3 | **Chamber sensor** | SHT45 breakout (Adafruit #5665 or equiv.) | I²C, 3.3 V; ±0.1 °C / ±1 % RH |
| 4 | **Peltier SSR** | SSR-40 DD (40 A DC-DC solid-state relay, 3–32 V control) | DC–DC only — not AC SSR |
| 5 | **PTC heater** | 12 V 50 W PTC ceramic heater with integrated 12 V fan, 87.5 × 60 × 42 mm (AliExpress) | ~4.2 A + fan (~0.2 A); fan and heater share one relay — both cycle together |
| 6 | **Heater relay** | 5 V relay module (e.g. SRD-05VDC-SL-C, 10 A rating) | Optocoupler-isolated board; 10 A rating > 4.2 A load ✓ |
| 8 | **Dehumidifier** | Compact thermoelectric dehumidifier (e.g. Ivation IVADM10) | 120 V AC |
| 9 | **Dehumidifier relay** | AC SSR or mechanical relay rated 10 A 120 V | Isolate mains from ESP32 |
| 10 | **Fan relay** | 5 V relay module | For fan power switching on boot |
| 11 | **12 V PSU** | Mean Well LRS-100-12 or fridge's existing 12 V rail | ≥ 8 A recommended (Peltier ~6 A + heater 4.2 A + fans) |
| 12 | **5 V PSU** | USB phone charger or Mean Well IRM-05-5 | Powers ESP32 and relay coils |
| 13 | **Misc** | 18 AWG wire, lever nuts (Wago 221), heat shrink | No 4.7 kΩ pull-up needed (no DS18B20) |

## GPIO Pinout

| GPIO | Function | Notes |
|---|---|---|
| 5 | Fan relay IN | Active HIGH |
| 18 | Peltier SSR-40 DD control | slow_pwm 20 s; active HIGH; 3.3 V compatible |
| 19 | Heater relay IN | slow_pwm 20 s; active HIGH |
| 21 | SDA (SHT45) | I²C |
| 22 | SCL (SHT45) | I²C |
| 23 | Dehumidifier relay IN | Active HIGH |

## Wiring Overview

```
                     ┌──────────────────────────────────────┐
                     │           ESP32-C6 DevKit            │
                     │                                      │
  SHT45 SDA ─────────┤ GPIO21 (SDA)                         │
  SHT45 SCL ─────────┤ GPIO22 (SCL)                         │
                     │                  GPIO5  ├────────── Fan Relay IN
                     │                  GPIO18 ├────────── Peltier SSR-40 DD IN
                     │                  GPIO19 ├────────── Heater Relay IN
                     │                  GPIO23 ├────────── Dehumidifier Relay IN
                     └──────────────────────────────────────┘

  12V PSU ──────────────── Peltier SSR OUT ────────── Peltier + terminal
          └──────────────── Fans (always on via relay)
          └──────────────── PTC Heater (via relay)

  Mains 120V ──────────── AC Relay OUT ─────────── Dehumidifier AC plug

  5V USB/PSU ──────────── ESP32 VIN
             └──────────── Relay board VCC (if 5V coil relay boards used)
```

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
