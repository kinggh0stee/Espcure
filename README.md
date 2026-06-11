# EspCure

Open-source DIY cannabis curing chamber controller built on ESPHome + ESP32. Inspired by the Cannatrol and the thermoelectric wine-cooler modification documented at [rollitup.org](https://www.rollitup.org/t/thermoelectric-wine-cooler-drying-and-curing-diy.1088980/). Base hardware is a Honeywell thermoelectric fridge with its original control board replaced by an ESP32.

## Features

- PID temperature control targeting 55 °F (12.8 °C)
- Bang-bang humidity control with adjustable setpoint and hysteresis
- Automated cure program: −1 % RH/day from 78 % → 60 % over 18 days
- Cold-plate frost protection (Peltier auto-disables below 35 °F / 1.5 °C)
- Home Assistant integration via native encrypted API
- PID autotune button for calibration after install
- OTA firmware updates, fallback WiFi AP, local web UI

## Hardware Required

- ESP32 DevKit v1
- SHT31-D breakout (chamber temp + RH)
- DS18B20 waterproof probe (cold plate frost guard)
- DC solid-state relay (Peltier control — **DC SSR, not AC**)
- 12 V PTC heater pad (20–30 W) + heatsink
- Compact dehumidifier (e.g. Ivation IVADM10)
- Relay module(s) for heater, dehumidifier, fans

Full BOM and wiring: [`docs/hardware.md`](docs/hardware.md)

## Quick Start

```bash
cp secrets.yaml.example secrets.yaml
# edit secrets.yaml
esphome config espcure.yaml    # validate
esphome run espcure.yaml       # flash (USB first time)
```

Full guide: [`docs/setup.md`](docs/setup.md)

## Documentation

| Doc | Contents |
|---|---|
| [`docs/hardware.md`](docs/hardware.md) | BOM, GPIO pinout, wiring diagram |
| [`docs/setup.md`](docs/setup.md) | Flash guide, HA integration, first-run checklist |
| [`docs/calibration.md`](docs/calibration.md) | Sensor offset calibration |
| [`docs/pid-tuning.md`](docs/pid-tuning.md) | PID autotune procedure + tuning log |
| [`docs/cure-programs.md`](docs/cure-programs.md) | Cure program logic + HA automation examples |

## License

MIT
