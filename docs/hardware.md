# Hardware

## Bill of Materials

| # | Component | Spec / Part | Notes |
|---|---|---|---|
| 1 | **Fridge** | Honeywell thermoelectric wine cooler | Remove original control board |
| 2 | **MCU** | ESP32 DevKit v1 (38-pin) | 3.3 V logic |
| 3 | **Chamber sensor** | SHT31-D breakout (Adafruit #2857 or equiv.) | I²C, 3.3 V |
| 4 | **Cold-plate sensor** | DS18B20 waterproof probe | 1-Wire, 4.7 kΩ pull-up to 3.3 V |
| 5 | **Peltier SSR** | DC solid-state relay, 3–32 V control, 40 A 12 V load (e.g. Crydom D1D40) | DC–DC only — not AC SSR |
| 6 | **PTC heater** | 12 V PTC heater pad, 20–30 W (e.g. uxcell 12V 30W PTC) | Mount on heatsink with fan |
| 7 | **Heater relay** | 5 V relay module (e.g. SRD-05VDC-SL-C) | Optocoupler-isolated board |
| 8 | **Dehumidifier** | Compact thermoelectric dehumidifier (e.g. Ivation IVADM10) | 120 V AC |
| 9 | **Dehumidifier relay** | AC SSR or mechanical relay rated 10 A 120 V | Isolate mains from ESP32 |
| 10 | **Fan relay** | 5 V relay module | For fan power switching on boot |
| 11 | **12 V PSU** | Mean Well LRS-100-12 or fridge's existing 12 V rail | ≥ 5 A for Peltier + heater + fans |
| 12 | **5 V PSU** | USB phone charger or Mean Well IRM-05-5 | Powers ESP32 and relay coils |
| 13 | **Misc** | 18 AWG wire, lever nuts (Wago 221), 4.7 kΩ resistor, heat shrink | — |

## GPIO Pinout

| GPIO | Function | Notes |
|---|---|---|
| 4 | DS18B20 data (1-Wire) | 4.7 kΩ pull-up to 3.3 V required |
| 5 | Fan relay IN | Active HIGH |
| 18 | Peltier SSR control | slow_pwm 20 s; active HIGH |
| 19 | PTC heater relay IN | slow_pwm 20 s; active HIGH |
| 21 | SDA (SHT31) | I²C |
| 22 | SCL (SHT31) | I²C |
| 23 | Dehumidifier relay IN | Active HIGH |

## Wiring Overview

```
                     ┌──────────────────────────────────────┐
                     │           ESP32 DevKit v1            │
                     │                                      │
  SHT31 SDA ─────────┤ GPIO21 (SDA)                         │
  SHT31 SCL ─────────┤ GPIO22 (SCL)                         │
  DS18B20  ──────────┤ GPIO4 (1-Wire)   GPIO5  ├────────── Fan Relay IN
  3.3V ──4.7kΩ──────┤                  GPIO18 ├────────── Peltier SSR IN
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

## Mounting the SHT31

Mount the SHT31 inside the chamber, away from the Peltier cold plate and away from the dehumidifier exhaust. Ideal position: center-rear of the interior air space, elevated off the floor. The SHT31 has slight self-heating (~1.5 °C at 3.3 V continuous); calibrate with an offset after install.

## Cold-Plate Probe Placement

Attach the DS18B20 waterproof probe directly to the Peltier cold plate (the metal fin assembly on the inside of the fridge door or liner). Use thermal tape or a small aluminum clamp. This is the frost guard — it must read the actual cold-plate temperature, not air temperature.

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
