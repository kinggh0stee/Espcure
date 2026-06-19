# EspCure

Open-source DIY cannabis curing chamber controller built on ESPHome + ESP32-C6. Inspired by the [Cannatrols](https://cannatrols.com/) and the thermoelectric wine-cooler modification documented at [rollitup.org](https://www.rollitup.org/t/thermoelectric-wine-cooler-drying-and-curing-diy.1088980/). Base hardware is a Honeywell thermoelectric fridge with its original control board replaced by an ESP32-C6.

## How it works

Two decoupled control loops: the **Peltier chases dew point / VPD** (cooling the cold plate below the dew point condenses moisture — this is the dehumidifier), and the **heater chases temperature** (a heat-only PID). There's no active temperature *cooling*, so the chamber floats a few degrees above ambient (typically ~17–19 °C) and the heater just holds the floor. A high-temperature safety ceiling forces the Peltier on if the chamber ever overheats.

## Features

- **Heat-only temperature PID** — PTC heater chases setpoint (default 15.6 °C); live-tunable Kp/Ki/Kd without reflashing
- **Peltier cold-plate dehumidification** — condenses moisture from air; no external dehumidifier relay
- **Dew Point humidity control** (default) — Cannatrol-style bang-bang on dew point °C; VPD mode exists in code but is hidden (`internal: true`)
- **Cannatrol 4+4 program** — 4 days dry at 12.2 °C DP → 4 days cure at 11.1 °C DP
- **10-Day Dry program** — proven dew-point recipe at 15.6 °C: 2-day ramp 15.6→13.9→12.2 °C DP, hold 12.2 °C (days 3–6), hold 11.1 °C (days 7–10), auto-off after day 10
- **One-tap presets** — Apply Dry Profile, Apply Cure Profile buttons
- **Dew point + VPD sensors** — derived from SHT45 readings via Magnus formula
- **Temperature safety ceiling** — forces Peltier cooling ON if chamber exceeds 27 °C regardless of humidity demand
- **Software frost floor** — Peltier auto-disables below 4 °C, heater aids recovery; no cold-plate sensor needed
- **SSD1306 OLED display** — 3-page cycling (temp/RH/DP/VPD, control settings, program status); BOOT button (GPIO9) cycles pages
- **WS2812 RGB LED** (GPIO8, built-in) — cure-progress indicator at 50% brightness: purple when idle (no program), fades blue→green during active program (by day), solid green when cured, white blink during frost guard (safety); toggled by **Status LED Enable** switch
- **Device-hosted web UI** at `http://espcure.local` — full React dashboard with entities organized into groups (Climate & Temperature, Humidity & Dew Point, Cure Programs, Status & Indicators, Setup & Tuning, Diagnostics); no HA required
- **Home Assistant integration** via encrypted native API; all entities with device_class + state_class
- **GitHub Actions CI** — `esphome config` validation on every PR
- OTA updates, fallback WiFi AP

## Hardware Required

- ESP32-C6 DevKitC-1
- SHT31 or SHT45 breakout (I²C 0x44 — chamber temp + RH; selectable via `sht_platform` substitution in `espcure.yaml`)
- 3× SSR-40 DD (fan rail GPIO5 / Peltier TEC GPIO18 / PTC heater GPIO19), `ledc` 15 Hz on the TEC + heater
- 12 V 50 W PTC ceramic heater with integrated fan
- 12 V → 5 V buck converter (LM2596 / MP1584EN) for the ESP32
- Thermoelectric fridge base with Peltier cold plate (~28 L, e.g. Honeywell wine cooler)

Full BOM and wiring: [`docs/hardware.md`](docs/hardware.md)

## Quick Start

**Linux / macOS:**
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt          # pins esphome==2026.5.3 (matches CI)
cp secrets.yaml.example secrets.yaml
# edit secrets.yaml with your WiFi credentials, API key, OTA password
esphome config espcure.yaml              # validate before flashing
esphome run espcure.yaml                 # flash via USB (first time)
```

**Windows (PowerShell):**
```powershell
py -m venv venv; .\venv\Scripts\Activate.ps1
pip install -r requirements.txt          # pins esphome==2026.5.3 (matches CI)
Copy-Item secrets.yaml.example secrets.yaml
# edit secrets.yaml with your WiFi credentials, API key, OTA password
esphome config espcure.yaml              # validate before flashing
esphome run espcure.yaml                 # flash via USB (first time)
```

Full guide (including key generation on both platforms): [`docs/setup.md`](docs/setup.md)

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
