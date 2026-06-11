# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## What this is

**EspCure** — an open-source DIY cannabis curing chamber controller built on ESPHome and ESP32-C6. Inspired by the Cannatrol and the thermoelectric wine-cooler modification documented at rollitup.org. The base hardware is a Honeywell thermoelectric (Peltier) fridge with its original control board bypassed and replaced by an ESP32-C6.

Capabilities:
- PID temperature control (default 55 °F / 12.8 °C)
- Dual humidity control modes: **RH mode** (rollitup-style, bang-bang on % RH) and **Dew Point mode** (Cannatrol-style, bang-bang on dew point °C)
- Dew point + VPD sensors derived from SHT45 readings
- Automated cure program: steps humidity down 1 %/day from 78 % → 60 %
- Software frost floor (disables Peltier if chamber air drops below configurable floor, default 4 °C)
- Home Assistant integration via native API
- OTA updates, fallback AP, local web UI

## Repository layout

```
espcure.yaml            Main ESPHome configuration
secrets.yaml.example    Template — copy to secrets.yaml (gitignored)
docs/
  hardware.md           BOM, pinout, wiring guide
  setup.md              First-flash and integration guide
  calibration.md        Sensor offset calibration procedure
  pid-tuning.md         PID autotune and manual tuning guide
  cure-programs.md      Cure program logic and HA automation examples
.claude/
  agents/               Sub-agent definitions (see below)
  settings.json         Permissions
```

## Primary config file

All ESPHome work lives in **`espcure.yaml`**. Key sections:

| Section | Purpose |
|---|---|
| `climate.pid` | Temperature PID — `kp`, `ki`, `kd` here |
| `output.slow_pwm` (peltier) | 20 s period; never reduce below 10 s |
| `output.slow_pwm` (heater) | 20 s period |
| `interval` (30 s) | Humidity/dew-point bang-bang loop (switches on `use_dew_point_control`) |
| `interval` (60 s) | Frost-guard loop |
| `time.on_time` (cron) | Daily cure step-down |
| `number.*_setpoint` | User-facing setpoints exposed to HA |

## Build & flash

```bash
# Install ESPHome (once)
pip install esphome

# Validate config
esphome config espcure.yaml

# First flash (USB)
esphome run espcure.yaml

# Subsequent OTA
esphome run espcure.yaml --device espcure.local
```

**Never flash without running `esphome config` first** — it catches YAML errors.

## Development rules

1. **Route work to the matching agent** before making non-trivial changes (see table below).
2. Validate with `esphome config espcure.yaml` after every edit.
3. All electrical/safety changes require `safety-reviewer` sign-off.
4. Keep `secrets.yaml.example` in sync with any new `!secret` keys added.
5. Don't hard-code WiFi credentials, API keys, or passwords — always use `!secret`.
6. The `slow_pwm` period for the Peltier must stay ≥ 10 s to avoid thermal cycling damage.
7. PID `kp`/`ki`/`kd` changes must be documented in `docs/pid-tuning.md`.

## Sub-agents

| Agent | Model | Role |
|---|---|---|
| `plan` | **opus** | Architecture, approach, significant design decisions |
| `esphome-dev` | sonnet | YAML edits, component config, automations, lambdas |
| `hardware-advisor` | **opus** | BOM, component selection, wiring, voltage/current safety |
| `pid-tuner` | sonnet | PID coefficient analysis, autotune interpretation, control loop |
| `safety-reviewer` | **opus** | Electrical safety, frost protection logic, thermal runaway review |
| `docs-writer` | haiku | README, hardware docs, setup guides, cure-program docs |
| `ha-integration` | haiku | Home Assistant dashboard YAML, HA automations, Lovelace cards |

### Mandatory workflow

1. For any non-trivial change: consult `plan` (opus) for approach.
2. Route implementation to the matching specialist agent.
3. Run `esphome config espcure.yaml` to validate.
4. Electrical or safety-touching changes → `safety-reviewer` before done.
5. Update relevant docs via `docs-writer` if behavior changed.

## Key constraints & gotchas

- **Peltier switching**: Use `slow_pwm` ≥ 10 s period only. Never use regular GPIO PWM — rapid switching destroys Peltier junctions.
- **DC SSR required**: The Peltier runs on 12 V DC. The SSR-40 DD is a DC-DC SSR. Do not substitute an AC SSR.
- **No cold-plate sensor**: There is no DS18B20. Frost protection is software-only: if `chamber_temp` drops below `min_chamber_temp` (default 4 °C), PID is disabled until chamber recovers 2 °C above the floor. The `frost_active` global tracks this state.
- **Humidity loop**: The dehumidifier's primary function is to raise internal temperature slightly, triggering the Peltier to activate and pull moisture through condensation on the cold plate — not direct dehumidification.
- **Cure program**: Driven by `time.homeassistant` cron (midnight). Requires HA time sync. Restarting ESPHome does not reset the day counter (`restore_value: true`).
- **Sensor calibration**: SHT45 self-heating is ~0.1–0.2 °C (much less than SHT31). Still calibrate with `offset` in `filters` after install.
- **Cannatrol dew-point philosophy**: The Cannatrol controls dew point, not raw RH. With `use_dew_point_control` ON, the dehumidifier is driven by `dew_point_setpoint` (°C). Cannatrol cure default is 11.1 °C (52 °F dew point). The `dew_point` sensor is calculated from SHT45 T + RH via Magnus formula — do not replace it with a direct sensor.
- **ESP32-C6 requires ESP-IDF**: The `framework: type: esp-idf` must not be changed to `arduino`. The C6 variant is not Arduino-compatible in ESPHome.
