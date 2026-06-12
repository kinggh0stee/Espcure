# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## What this is

**EspCure** — an open-source DIY cannabis curing chamber controller built on ESPHome and ESP32-C6. Inspired by the Cannatrol and the thermoelectric wine-cooler modification documented at rollitup.org. The base hardware is a Honeywell thermoelectric (Peltier) fridge with its original control board bypassed and replaced by an ESP32-C6.

Capabilities:
- PID temperature control with live tunable Kp/Ki/Kd (default 55 °F / 12.8 °C)
- **Three humidity control modes**: RH mode (bang-bang % RH), Dew Point mode (Cannatrol-style bang-bang on °C), VPD mode (bang-bang on kPa — dehumidifier only)
- Dew point + VPD derived sensors; humidity error, dew-point error diagnostic sensors
- **18-day step-down program** (RH mode): −1 %/day from 78 % → 60 %
- **Cannatrol 4+4 program** (dew-point mode): 4 days dry at 12.2 °C DP → 4 days cure at 11.1 °C DP
- **One-tap presets**: Dry Profile, Cure Profile, Cold-Plate Profile buttons
- Chamber Status text sensor (Cooling / Heating / Idle / Frost Guard)
- Software frost floor (disables Peltier if chamber air drops below configurable floor, default 4 °C)
- **SSD1306 OLED display**: 3-page cycling (temp/RH/DP/VPD, control settings, program status); BOOT button (GPIO9) cycles pages manually
- **WS2812 RGB LED** (GPIO8, built-in): cooling=blue, heating=red(dim), idle=green(very dim), frost=white blink
- Home Assistant integration via encrypted native API (device_class + state_class on all sensors)
- Device-hosted web UI at `http://espcure.local` — `web_server` v3, dark mode toggle, no HA required
- OTA updates, fallback AP
- GitHub Actions CI validates `esphome config` on every PR

## Repository layout

```
espcure.yaml            Main ESPHome configuration
secrets.yaml.example    Template — copy to secrets.yaml (gitignored)
requirements.txt        Python deps — pins esphome==2026.5.3 for CI parity
requirements-docs.txt   Docs deps — pins mkdocs-material>=9.5
mkdocs.yml              MkDocs config; site published to GitHub Pages
README.md               Project overview and feature list
CHANGELOG.md            Release history (Keep a Changelog format)
TODO.md                 Project TODO list (prioritized)
docs/
  index.md              Docs home page (MkDocs entry point)
  hardware.md           BOM, pinout, wiring guide
  setup.md              First-flash and HA integration guide
  calibration.md        Sensor offset calibration procedure
  pid-tuning.md         PID autotune and manual tuning guide
  cure-programs.md      Cure programs (18-day + Cannatrol 4+4) and HA automations
  ha-dashboard.yaml     Ready-to-import Lovelace dashboard (5 tabs)
  display-plan.md       Display hardware options, wiring, ESPHome config skeleton
  stylesheets/
    extra.css           Custom CSS for MkDocs Material theme
  overrides/
    home.html           Custom home-page template
.github/
  workflows/
    validate.yml        ESPHome config validation CI (PRs + main pushes)
    docs.yml            Auto-deploy MkDocs to GitHub Pages on push to main
.claude/
  agents/               Sub-agent definitions (see below)
  settings.json         Permissions
```

## Primary config file

All ESPHome work lives in **`espcure.yaml`**. Key sections:

| Section | Purpose |
|---|---|
| `climate.pid` | Temperature PID — defaults Kp=0.35, Ki=0.005, Kd=1.2; deadband ±0.5 °C |
| `output.slow_pwm` (peltier) | 20 s period; never reduce below 10 s |
| `output.slow_pwm` (heater) | 20 s period |
| `interval` (30 s) | Humidity/dew-point bang-bang loop (switches on `use_dew_point_control`) |
| `interval` (60 s) | Frost-guard loop |
| `interval` (2 s) | Status LED update loop — polls PID action, drives WS2812 colour |
| `switch.fan_relay` | GPIO5 — fan rail SSR; always turns ON at boot (`on_boot`) |
| `switch.dehumidifier_relay` | GPIO23 — bang-bang controlled by the 30 s humidity loop |
| `time.on_time` (cron) | Midnight cron — 18-day step + Cannatrol 4+4 advance |
| `number.*_setpoint` | User-facing setpoints exposed to HA and web UI |
| `number.pid_k*` | Live PID tuning — `on_value` calls `set_control_parameters` |
| `number.vpd_setpoint` / `number.vpd_hysteresis` | VPD control setpoints (kPa) for VPD mode |
| `switch.cure_program_active` | 18-day RH step-down program |
| `switch.cannatrol_program_active` | Cannatrol 4+4 dew-point program |
| `switch.use_dew_point_control` | Dew Point mode toggle (mutual-exclusive with VPD mode) |
| `switch.use_vpd_control` | VPD mode toggle (mutual-exclusive with dew-point mode) |
| `button.apply_*_profile` | One-tap profile presets |
| `text_sensor.chamber_status` | Human-readable operating state |
| `light.status_led` | WS2812 RGB LED (GPIO8) — color reflects PID action |
| `display.oled` (pages) | SSD1306 OLED, 3-page cycling; `page_button` GPIO9 cycles |
| `esp32_improv` | BLE WiFi provisioning; BOOT button (GPIO9) is the authorizer |
| `improv_serial` | Serial WiFi provisioning (USB fallback) |

## Build & flash

```bash
# Install ESPHome — use requirements.txt to match the CI-pinned version
pip install -r requirements.txt

# Validate config
esphome config espcure.yaml

# First flash (USB)
esphome run espcure.yaml

# Subsequent OTA
esphome run espcure.yaml --device espcure.local
```

**Never flash without running `esphome config` first** — it catches YAML errors.

**Always install with `pip install -r requirements.txt`** — pins `esphome==2026.5.3`, matching `validate.yml`. Installing a different version can produce parse differences that only surface in CI.

### Docs site

```bash
# Local preview
mkdocs serve

# Deploy to GitHub Pages (maintainers only — CI does this automatically)
mkdocs gh-deploy
```

The docs site is automatically deployed by `.github/workflows/docs.yml` on every push to `main`.

## GitHub Actions CI

| Workflow | File | Trigger | What it does |
|---|---|---|---|
| ESPHome Validate | `.github/workflows/validate.yml` | PR or push to `main` touching `espcure.yaml` or `secrets.yaml.example` | Writes a placeholder `secrets.yaml` with dummy values, then runs `esphome config espcure.yaml` |
| Deploy Docs | `.github/workflows/docs.yml` | Push to `main` (any file) or manual `workflow_dispatch` | Installs `requirements-docs.txt`, runs `mkdocs gh-deploy --force` to GitHub Pages |

No real credentials are stored in the repo. The dummy `api_encryption_key` used in CI is a valid base64-encoded 32-byte value so the ESPHome parser accepts it.

## Development rules

1. **Route work to the matching agent** before making non-trivial changes (see table below).
2. Validate with `esphome config espcure.yaml` after every edit.
3. All electrical/safety changes require `safety-reviewer` sign-off.
4. Keep `secrets.yaml.example` in sync with any new `!secret` keys added.
5. Don't hard-code WiFi credentials, API keys, or passwords — always use `!secret`.
6. The `slow_pwm` period for the Peltier must stay ≥ 10 s to avoid thermal cycling damage.
7. PID `kp`/`ki`/`kd` changes must be documented in `docs/pid-tuning.md`.
8. Install dependencies with `pip install -r requirements.txt` (not bare `pip install esphome`) to stay in sync with the CI-pinned ESPHome version.
9. Update `CHANGELOG.md` for any user-facing change — new entities, behaviour changes, removals. Follow Keep a Changelog format (`### Added / Changed / Fixed / Removed` under `## [Unreleased]`).

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
| `senior-reviewer` | **opus** | Final review gate for major changes — audits correctness, safety compliance, secrets hygiene, and doc sync |
| `ci-checker` | sonnet | Pre-push validation — runs `esphome config`, checks safety invariants, scans for leaked secrets |

### Mandatory workflow

1. For any non-trivial change: consult `plan` (opus) for approach.
2. Route implementation to the matching specialist agent.
3. Run `ci-checker` to validate config, secrets, and safety invariants before pushing.
4. Electrical or safety-touching changes → `safety-reviewer` before done.
5. Update relevant docs via `docs-writer` if behavior changed.
6. Run `senior-reviewer` as the final gate before any major change is merged.

## Key constraints & gotchas

- **Peltier switching**: Use `slow_pwm` ≥ 10 s period only. Never use regular GPIO PWM — rapid switching destroys Peltier junctions.
- **All 3 outputs use SSR-40 DD**: Fan rail (GPIO5), TEC cooling (GPIO18), heater element (GPIO19) — all DC-DC solid-state relays. No mechanical relay modules in this build. SSR-40 DDs must be on heatsinks when carrying > 5 A.
- **Dehumidifier relay**: GPIO23 — bang-bang controlled by the 30 s `interval` loop. Not part of the SSR-40 DD trio; it is the external dehumidifier plug relay. Restore mode is `RESTORE_DEFAULT_OFF`.
- **3.3 V GPIO → SSR-40 DD**: ESP32-C6 outputs 3.3 V; SSR-40 DD spec minimum is 3 V. Verify each SSR triggers reliably at 3.3 V before final install. If marginal, add a 2N2222 NPN driver on the control line.
- **No cold-plate sensor**: There is no DS18B20. Frost protection is software-only: if `chamber_temp` drops below `min_chamber_temp` (default 4 °C), PID is disabled until chamber recovers 2 °C above the floor. The `frost_active` global tracks this state.
- **GPIO reference**:

  | GPIO | Function |
  |---|---|
  | GPIO5 | Fan rail SSR-40 DD (always ON at boot) |
  | GPIO8 | WS2812 RGB LED (built-in DevKitC-1 LED) |
  | GPIO9 | BOOT / page button — OLED page cycle + BLE provisioning authorizer |
  | GPIO18 | Peltier (cooling) SSR-40 DD — `slow_pwm` 20 s period |
  | GPIO19 | Heater SSR-40 DD — `slow_pwm` 20 s period |
  | GPIO21 | I²C SDA (SHT45 + SSD1306) |
  | GPIO22 | I²C SCL (SHT45 + SSD1306) |
  | GPIO23 | Dehumidifier relay |

- **Shared I²C bus**: SHT45 sensor (address `0x44`) and SSD1306 OLED (address `0x3C`) share GPIO21/GPIO22. Do not add a second `i2c:` block — add new devices to the existing bus with their own `address:` key.
- **Humidity loop**: The dehumidifier's primary function is to raise internal temperature slightly, triggering the Peltier to activate and pull moisture through condensation on the cold plate — not direct dehumidification.
- **Cure programs**: Both the 18-day and Cannatrol 4+4 programs are driven by `time.homeassistant` cron (midnight). Require HA time sync. Day counters use `restore_value: true` — restarting ESPHome does not reset them. Enabling one program automatically disables the other.
- **Cannatrol 4+4 program**: `cannatrol_phase` global (0=dry, 1=cure) tracks which phase is active. Phase transitions happen at midnight on day 5. The `cannatrol_program_status` text sensor exposes progress to both HA and the web UI.
- **Sensor calibration**: SHT45 self-heating is ~0.1–0.2 °C (much less than SHT31). Still calibrate with `offset` in `filters` after install.
- **Cannatrol dew-point philosophy**: The Cannatrol controls dew point, not raw RH. With `use_dew_point_control` ON, the dehumidifier is driven by `dew_point_setpoint` (°C). Cannatrol cure default is 11.1 °C (52 °F dew point). The `dew_point` sensor is calculated from SHT45 T + RH via Magnus formula — do not replace it with a direct sensor.
- **Three humidity control modes**: RH mode (default), Dew Point mode, VPD mode. Only one active at a time — `use_vpd_control` and `use_dew_point_control` are mutually exclusive (each `on_turn_on` turns off the other). All three modes control only the dehumidifier relay — there is no humidifier in this build.
- **ESP32-C6 requires ESP-IDF**: The `framework: type: esp-idf` must not be changed to `arduino`. The C6 variant is not Arduino-compatible in ESPHome.
- **BLE provisioning**: `esp32_improv` is enabled with `authorizer: page_button` (GPIO9 BOOT button). Hold the BOOT button while a phone scans for the device to authorize WiFi provisioning. `improv_serial` provides the same over USB serial.
