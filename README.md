# EspCure

Open-source DIY cannabis curing chamber controller built on ESPHome + ESP32-C6. Inspired by the [Cannatrol](https://cannatrol.com/) and the thermoelectric wine-cooler modification documented at [rollitup.org](https://www.rollitup.org/t/thermoelectric-wine-cooler-drying-and-curing-diy.1088980/). Base hardware is a Honeywell thermoelectric fridge with its original control board replaced by an ESP32-C6.

## How it works

Two decoupled control loops: the **Peltier chases dew point / VPD** (cooling the cold plate below the dew point condenses moisture — this is the dehumidifier), and the **heater chases temperature** (a heat-only PID). There's no active temperature *cooling*, so the chamber floats a few degrees above ambient (typically ~63–67 °F) and the heater just holds the floor. A high-temperature safety ceiling forces the Peltier on if the chamber ever overheats.

## Features

- **Heat-only temperature PID** — PTC heater chases setpoint (default 60 °F / 15.6 °C); live-tunable Kp/Ki/Kd without reflashing
- **Peltier cold-plate dehumidification** — condenses moisture from air; no external dehumidifier relay
- **Two humidity control modes** (mutually exclusive):
  - **Dew Point mode** (default) — Cannatrol-style bang-bang on dew point °C
  - **VPD mode** — bang-bang on Vapor Pressure Deficit (kPa)
- **Cannatrol 4+4 program** — 4 days dry at 12.2 °C DP (54 °F) → 4 days cure at 11.1 °C DP (52 °F)
- **10-Day Dry program** — proven dew-point recipe at 60 °F: 2-day ramp 60→57→54 °F DP, hold 54 °F (days 3–6), hold 52 °F (days 7–10), auto-off after day 10
- **One-tap presets** — Apply Dry Profile, Apply Cure Profile buttons
- **Dew point + VPD sensors** — derived from SHT45 readings via Magnus formula
- **Temperature safety ceiling** — forces Peltier cooling ON if chamber exceeds 27 °C (80 °F) regardless of humidity demand
- **Software frost floor** — Peltier auto-disables below 4 °C (39 °F), heater aids recovery; no cold-plate sensor needed
- **SSD1306 OLED display** — 3-page cycling (temp/RH/DP/VPD, control settings, program status); BOOT button (GPIO9) cycles pages
- **WS2812 RGB LED** (GPIO8, built-in) — cooling=blue, heating=red, idle=green(dim), frost=white blink
- **Device-hosted web UI** at `http://espcure.local` — full React dashboard with entities organized into groups (Climate, Humidity, VPD, Programs, PID, Hardware, Diagnostics); no HA required
- **Home Assistant integration** via encrypted native API; all entities with device_class + state_class
- **GitHub Actions CI** — `esphome config` validation on every PR
- OTA updates, fallback WiFi AP

## Hardware Required

- ESP32-C6 DevKitC-1
- SHT45 breakout (I²C 0x44 — chamber temp + RH)
- 3× SSR-40 DD (fan rail GPIO5 / Peltier TEC GPIO18 / PTC heater GPIO19), `ledc` 15 Hz on the TEC + heater
- 12 V 50 W PTC ceramic heater with integrated fan
- 12 V → 5 V buck converter (LM2596 / MP1584EN) for the ESP32
- Thermoelectric fridge base with Peltier cold plate (~28 L, e.g. Honeywell wine cooler)

Full BOM and wiring: [`docs/hardware.md`](docs/hardware.md)

## Quick Start

```bash
cp secrets.yaml.example secrets.yaml
# edit secrets.yaml with your WiFi credentials, API key, OTA password
esphome config espcure.yaml    # validate before flashing
esphome run espcure.yaml       # flash via USB (first time)
```

Full guide: [`docs/setup.md`](docs/setup.md)

## Documentation

| Doc | Contents |
|---|---|
| [`docs/hardware.md`](docs/hardware.md) | BOM, GPIO pinout, wiring guide |
| [`docs/setup.md`](docs/setup.md) | Flash guide, HA integration, first-run checklist |
| [`docs/calibration.md`](docs/calibration.md) | SHT45 offset calibration procedure |
| [`docs/pid-tuning.md`](docs/pid-tuning.md) | Heat-only PID autotune + tuning log |
| [`docs/cure-programs.md`](docs/cure-programs.md) | Cannatrol 4+4 + 10-Day Dry programs, HA automations |
| [`docs/ha-dashboard.yaml`](docs/ha-dashboard.yaml) | Ready-to-import Lovelace dashboard (5 tabs) |
| [`docs/display-plan.md`](docs/display-plan.md) | OLED display wiring + TFT upgrade path |

## License

MIT
