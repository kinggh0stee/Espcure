# EspCure

Open-source DIY cannabis curing chamber controller built on ESPHome + ESP32-C6. Inspired by the [Cannatrol](https://cannatrol.com/) and the thermoelectric wine-cooler modification documented at [rollitup.org](https://www.rollitup.org/t/thermoelectric-wine-cooler-drying-and-curing-diy.1088980/). Base hardware is a Honeywell thermoelectric fridge with its original control board replaced by an ESP32-C6.

## Features

- **PID temperature control** — Peltier (cool) + PTC heater (heat), default 55 °F / 12.8 °C; live-tunable Kp/Ki/Kd without reflashing
- **Three humidity control modes** (mutually exclusive):
  - **RH mode** — rollitup-style bang-bang on % RH
  - **Dew Point mode** — Cannatrol-style bang-bang on dew point °C
  - **VPD mode** — bang-bang on Vapor Pressure Deficit (kPa)
- **18-day cure program** — −1 %/day from 78 % → 60 % RH (rollitup method)
- **Cannatrol 4+4 program** — 4 days dry at 12.2 °C DP → 4 days cure at 11.1 °C DP
- **One-tap presets** — Dry Profile, Cure Profile, Cold-Plate Profile buttons
- **Dew point + VPD sensors** — derived from SHT45 readings via Magnus formula
- **Software frost floor** — Peltier auto-disables below 4 °C, no cold-plate sensor needed
- **SSD1306 OLED display** — 3-page cycling (temp/RH/DP/VPD, control settings, program status); BOOT button (GPIO9) cycles pages
- **WS2812 RGB LED** (GPIO8, built-in) — cooling=blue, heating=red(dim), idle=green(dim), frost=white blink
- **Device-hosted web UI** at `http://espcure.local` — full React dashboard, no HA required
- **Home Assistant integration** via encrypted native API; all entities with device_class + state_class
- **GitHub Actions CI** — `esphome config` validation on every PR
- OTA updates, fallback WiFi AP

## Hardware Required

- ESP32-C6 DevKitC-1
- SHT45 breakout (I²C 0x44 — chamber temp + RH)
- 3× SSR-40 DD (fan rail GPIO5 / Peltier TEC GPIO18 / PTC heater GPIO19)
- 12 V PTC heater pad (20–50 W) with heatsink
- Compact dehumidifier (e.g. Ivation IVADM10) — optional, relay on GPIO23
- Thermoelectric fridge base (Peltier wine cooler ~28 L)

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
| [`docs/pid-tuning.md`](docs/pid-tuning.md) | PID autotune procedure + tuning log |
| [`docs/cure-programs.md`](docs/cure-programs.md) | 18-day + Cannatrol 4+4 programs, HA automations |
| [`docs/ha-dashboard.yaml`](docs/ha-dashboard.yaml) | Ready-to-import Lovelace dashboard (5 tabs) |
| [`docs/display-plan.md`](docs/display-plan.md) | OLED display wiring + TFT upgrade path |

## License

MIT
