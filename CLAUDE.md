# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## What this is

**EspCure** — an open-source DIY cannabis curing chamber controller built on ESPHome and ESP32-C6. Inspired by the Cannatrol and the thermoelectric wine-cooler modification documented at rollitup.org. The base hardware is a Honeywell thermoelectric (Peltier) fridge with its original control board bypassed and replaced by an ESP32-C6.

**Control topology** (key mental model): the **Peltier chases dew point / VPD** (cold-plate condensation is the dehumidifier), and the **heater chases temperature** (heat-only PID). There is no active temperature *cooling* — chamber temp floats (typically ~17–19 °C); the heater only holds the floor.

Capabilities:
- **Selectable chamber sensor**: SHT31 (`sht3xd`) or SHT45 (`sht4x`), both at I²C 0x44, chosen via the `sht_platform` substitution at the top of `espcure.yaml`. No wiring change. **SHT45 (`sht4x`) is the shipped default**; the SHT31 lines are kept commented directly below for a one-step swap-back.
- **Heat-only PID** temperature control with live tunable Kp/Ki/Kd (default target 17.2 °C / 63 °F). Heater rarely runs.
- **Peltier cold-plate dehumidification** — the TEC is bang-bang driven (15 Hz full-on/off) by the active humidity loop; there is no external dehumidifier relay
- **Humidity control by dew point** (bang-bang on °C, hysteresis default ±0.1 °C). A VPD mode exists in the code but is `internal: true` (hidden from the web UI and HA, not user-selectable) — see the web-UI declutter note below
- Dew point derived sensor (+ an internal VPD sensor, still computed but no longer shown anywhere); dew-point error diagnostic sensor
- **Renameable / multi-unit** — `device_name`/`friendly_name` substitutions set the mDNS hostname and HA entity prefix per unit; optional `mac_suffix: "true"` appends the MAC for batch flashing. `fw_version` substitution is the single source of truth for the firmware version (feeds `esphome.project.version` + the Firmware Version text sensor).
- **10-day dry program** (dew point): day 1 ramps 15.6→12.2 °C DP, days 2–5 hold 12.2 °C, days 6–9 hold 11.1 °C, day 10 auto-off
- **High-temp safety ceiling** (`max_chamber_temp`, default 27 °C): forces the Peltier on above the limit since the heat-only PID can't cool
- Chamber Status text sensor (Cooling / Heating / Idle / Frost Guard)
- Software frost floor (forces Peltier off if chamber air drops below configurable floor, default 4 °C; heater keeps running)
- **SSD1306 OLED display**: 3-page cycling (page 1: temp/RH large + dew point vs setpoint + DP error/status + context-aware bottom row; page 2: control settings; page 3: program status); BOOT button (GPIO9) cycles pages manually. No VPD on the display anymore.
- **WS2812 RGB LED** (GPIO8, built-in) — **cure-progress indicator** at half power: idle=purple, active program fades **blue→green by day**, cured=solid green, frost=white blink (safety override). The light is `internal: true`; the **Status LED Enable** switch is the single on/off control. Painted by the `paint_status_led` script.
- Home Assistant integration via encrypted native API (device_class + state_class on all sensors); two ready-to-import Lovelace dashboards — `docs/ha-dashboard.yaml` (zero dependencies) and `docs/ha-dashboard-mushroom.yaml` (Mushroom/HACS edition)
- Diagnostic sensors: Firmware Version, Peltier (Dehumidify) Duty (%), Dew Point Error, PID Heat Output, PID Integral, uptime, WiFi signal
- Device-hosted web UI at `http://espcure.local` — `web_server` v3, dark mode toggle, entities in 6 sorting groups (Climate & Temperature, Humidity & Dew Point, Cure Programs, Status & Indicators, Setup & Tuning, Diagnostics); no HA required. **Web-UI declutter:** `entity_category: config`/`diagnostic` does NOT hide entities from the device web page (it only tucks them away in HA), so the page is decluttered by (a) grouping set-once knobs into the bottom "Setup & Tuning" + "Diagnostics" groups and (b) `internal: true` on never-used entities (the whole VPD suite, the `page_button` BOOT sensor, the `humidity_control_mode` text) — `internal: true` removes from BOTH the web page and HA
- OTA updates, fallback AP
- GitHub Actions CI validates `esphome config` and **compiles both sensor variants** (SHT31 + SHT45) on every PR

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
  cure-programs.md      Cure programs (10-day dry) and HA automations
  ha-dashboard.yaml     Ready-to-import Lovelace dashboard (zero HACS dependencies)
  ha-dashboard-mushroom.yaml  Alternative dashboard built on HACS cards (Mushroom, mini-graph-card, ApexCharts)
  display-plan.md       Display hardware options, wiring, ESPHome config skeleton
  wiring_diagrams.py    Pillow script that renders wiring_control.png + wiring_power.png
  wiring_control.png    Control-side wiring diagram (embedded in hardware docs)
  wiring_power.png      12 V power-side wiring diagram
  sht_wiring.py         Pillow script that renders sht_wiring.png (chamber-sensor wiring)
  sht_wiring.png        SHT45/SHT31 wiring diagram
  assets/
    favicon.svg         Docs site favicon
  stylesheets/
    extra.css           Custom CSS for MkDocs Material theme
  overrides/
    home.html           Custom home-page template
.github/
  workflows/
    validate.yml        ESPHome CI: `esphome config` + matrix compile of both sensor variants (PRs + main pushes)
    docs.yml            Auto-deploy MkDocs to GitHub Pages on push to main
.claude/
  agents/               Sub-agent definitions (see below)
  settings.json         Permissions
```

## Primary config file

All ESPHome work lives in **`espcure.yaml`**. Key sections:

| Section | Purpose |
|---|---|
| `substitutions` (device identity) | `device_name`/`friendly_name` — per-unit hostname (`http://<device_name>.local`), HA entity prefix, setup-AP SSID. `mac_suffix` (default `"false"`) appends the MAC for batch flashing. `fw_version` — single source of truth for the firmware version; **bump it on every release** (feeds `esphome.project.version` + the Firmware Version text sensor). |
| `substitutions.sht_platform` | Chamber sensor select: `sht3xd` (SHT31) or `sht4x` (SHT45); **ships as `sht4x`** with the SHT31 lines commented inline. Swap also sets the `sht_heater_on`/`sht_heater_off` substitutions (heater API differs) — no lambda editing. CI compiles both variants. |
| `wifi.power_save_mode: none` | Keeps the radio always-on. Do NOT remove — ESP-IDF's default modem sleep gets the device evicted by some APs (~15 min disconnect flaps, notably Ubiquiti). |
| `climate.pid` | **Heat-only** temperature PID (heater chases temp), named "Temperature Control" — defaults Kp=0.35, Ki=0.005, Kd=1.2; deadband ±0.5 °C; default target 17.2 °C (63 °F). On boot it is set to `mode: HEAT`. |
| `output.ledc` (peltier) | 15 Hz; both TECs in parallel on GPIO18. **Not a PID output** — driven directly by the 30 s humidity loop via `set_level(1.0/0.0)`. |
| `output.ledc` (heater) | 15 Hz; PTC element on GPIO19; `heat_output` of the PID |
| `interval` (30 s) | Dew-point/VPD bang-bang loop — **drives the Peltier**. Priority: frost guard → high-temp ceiling → VPD → Dew Point → off |
| `interval` (60 s) | Frost-guard loop — forces Peltier off below the floor; heater keeps running |
| `interval` (2 s) | Fan control + LED refresh — fan ON when a cure program is active (`dry10_program_active`) **or** `peltier_cooling` **or** heater heating (continuous circulation during programs); then calls the `paint_status_led` script. The LED painter is **edge-triggered** via the `led_state` global and gated by `switch.status_led_enable`. |
| `switch.fan_relay` | GPIO5 — fan rail SSR; runs continuously while a cure program is active, else ON when Peltier cooling or heater heating. Always commanded ON in the same lambda as the Peltier (hot-side airflow). |
| `switch.status_led_enable` | Gates the 2 s status-LED loop (default ON). OFF turns the WS2812 off and stops the loop driving it; fan control is unaffected. |
| `time.on_time` (cron) | Midnight cron — 10-day dry step |
| `number.*_setpoint` | User-facing setpoints exposed to HA and web UI. `dew_point_hysteresis` default 0.1 °C (`restore_value: true` — existing units keep their stored value across OTA updates) |
| `number.min_chamber_temp` / `number.max_chamber_temp` | Frost floor (default 4 °C) and high-temp safety ceiling (default 27 °C) |
| `number.pid_k*` | Live PID tuning — `on_value` calls `set_control_parameters` |
| `number.vpd_setpoint` / `number.vpd_hysteresis` | VPD control setpoints (kPa) for VPD mode |
| `global.peltier_cooling` | bool — single source of truth for "Peltier is condensing" (float outputs can't be read back) |
| `switch.dry10_program_active` | 10-day dew-point dry program |
| `switch.use_dew_point_control` | Dew Point mode toggle (default ON; mutual-exclusive with VPD mode) |
| `switch.use_vpd_control` | VPD mode toggle — now `internal: true` (hidden from web UI + HA, not selectable). VPD branch in the 30 s loop is dead-but-harmless. Kept for one-line revert. |
| `button` (Autotune / Restart / Clear Sensor Condensation) | PID autotune, controller restart, sensor condensation-clear. Heater statements come from `sht_heater_on`/`sht_heater_off` substitutions — a real heater pulse on SHT31, a no-op fresh-read on SHT45 (no on-demand heater API). |
| `text_sensor.chamber_status` | Human-readable operating state (Cooling / Heating / Idle / Frost Guard) |
| `web_server.sorting_groups` | 6 UI groups (Climate & Temperature, Humidity & Dew Point, Cure Programs, Status & Indicators, Setup & Tuning, Diagnostics) — every visible entity sets `sorting_group_id` + `sorting_weight`. Essentials on top; all `entity_category: config` knobs cluster in "Setup & Tuning", diagnostics last. NOTE: `entity_category` does NOT hide entities from the web page (HA-only); web declutter = grouping + `internal: true`. |
| `light.status_led` | WS2812 RGB LED (GPIO8), `internal: true` — driven only by the `paint_status_led` script. On/off via `switch.status_led_enable` (the single user control). |
| `script.paint_status_led` | Shared LED painter = **cure-progress**: idle purple@0.5, active program fades blue→green (`rgb(0, day/total, 1-day/total)`; total 10), `cure_complete` → solid green, frost → white blink (priority override). Called by the 2 s interval, instantly by the `status_led_enable` switch and the day-counter `on_value`, and edge-triggered via `led_state` (key encodes program+day) so the Frost Blink pulse isn't restarted. |
| `global.cure_complete` | bool (restored) — set when a program auto-completes (final-day cron branch), cleared on program start. Holds the LED solid green ("cured") after the program switches off. |
| `text_sensor` (Firmware Version) | Diagnostic sensor showing `${fw_version}` on the web UI + HA — confirms what's flashed without reading boot logs |
| `display.oled` (pages) | SSD1306 OLED, 3-page cycling; `page_button` GPIO9 cycles. Page 1: T+RH large, DP vs SP, DP error + chamber status, context-aware bottom row (frost / program day + temp target / standby). No VPD shown. |
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

On **Windows**, the same commands work from PowerShell inside a venv (`py -m venv venv; .\venv\Scripts\Activate.ps1`); if `esphome` isn't on PATH, call it as `py -m esphome config espcure.yaml`. Use `Copy-Item secrets.yaml.example secrets.yaml` instead of `cp`. See `docs/setup.md` for the full cross-platform flow.

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
| ESPHome Validate | `.github/workflows/validate.yml` | PR or push to `main` touching `espcure.yaml`, `secrets.yaml.example`, `requirements.txt`, or the workflow itself | Writes a placeholder `secrets.yaml`, runs `esphome config espcure.yaml`, then a **matrix compile job** builds firmware for both `sht_platform` values (SHT31 + SHT45) — the SHT45 run overrides the heater substitutions to `";"`. PlatformIO/ESP-IDF toolchain is cached. |
| Deploy Docs | `.github/workflows/docs.yml` | Push to `main` (any file) or manual `workflow_dispatch` | Installs `requirements-docs.txt`, runs `mkdocs gh-deploy --force` to GitHub Pages |

No real credentials are stored in the repo. The dummy `api_encryption_key` used in CI is a valid base64-encoded 32-byte value so the ESPHome parser accepts it.

## Development rules

1. **Route work to the matching agent** before making non-trivial changes (see table below).
2. Validate with `esphome config espcure.yaml` after every edit.
3. All electrical/safety changes require `safety-reviewer` sign-off.
4. Keep `secrets.yaml.example` in sync with any new `!secret` keys added.
5. Don't hard-code WiFi credentials, API keys, or passwords — always use `!secret`.
6. The Peltier (`peltier_output`, GPIO18) must have exactly **one writer** — the 30 s/60 s lambdas. Never add it back as a climate `cool_output`. Whenever it is set to `1.0`, the fan must be commanded ON in the same lambda (hot-side airflow).
7. PID `kp`/`ki`/`kd` changes must be documented in `docs/pid-tuning.md`.
8. Install dependencies with `pip install -r requirements.txt` (not bare `pip install esphome`) to stay in sync with the CI-pinned ESPHome version.
9. Update `CHANGELOG.md` for any user-facing change — new entities, behaviour changes, removals. Follow Keep a Changelog format (`### Added / Changed / Fixed / Removed` under `## [Unreleased]`).
10. Any non-ASCII glyph in a `text_sensor` or `display` lambda must be written as terminated hex byte escapes (e.g. `\xc2\xb0""C` for `°C`). See the UTF-8 gotcha below — an unterminated escape produces invalid UTF-8 that crashes the HA API connection.
11. New entities should declare a `web_server: sorting_group_id` + `sorting_weight` so they land in the right web-UI group.
12. Bump the `fw_version` substitution (top of `espcure.yaml`) on every release — it is the single source of truth for the version shown in boot logs, HA device info, and the Firmware Version sensor.

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

- **Peltier and heater outputs**: Both use `ledc` at 15 Hz (`peltier_output` GPIO18, `heater_output` GPIO19). At 15 Hz the TEC junction sees average power rather than thermal cycling, which reduces junction fatigue vs slow_pwm. Do not switch these to `slow_pwm` or reduce below ~10 Hz.
- **3 outputs use SSR-40 DD**: Fan rail (GPIO5), TEC cooling (GPIO18), heater element (GPIO19) — all DC-DC solid-state relays. No mechanical relay modules. SSR-40 DDs must be on heatsinks when carrying > 5 A. GPIO23 (formerly a dehumidifier relay) is now free/unused.
- **3.3 V GPIO → SSR-40 DD**: ESP32-C6 outputs 3.3 V; SSR-40 DD spec minimum is 3 V. Verify each SSR triggers reliably at 3.3 V before final install. If marginal, add a 2N2222 NPN driver on the control line.
- **Heat-only PID / no active cooling**: the PID only drives the heater. Temperature has no active cooling path — the chamber floats (typically ~17–19 °C) and the heater holds the floor. The **only** downward authority is the humidity-driven Peltier plus the high-temp safety ceiling (`max_chamber_temp`, default 27 °C), which forces the Peltier on above the limit. Do not re-add `cool_output` to the PID.
- **No cold-plate sensor**: There is no DS18B20. Frost protection is software-only: if `chamber_temp` drops below `min_chamber_temp` (default 4 °C), the **Peltier is forced off** until the chamber recovers 2 °C above the floor. The heat-only PID keeps running (heating aids recovery). The `frost_active` global tracks this state and short-circuits the 30 s loop.
- **GPIO reference**:

  | GPIO | Function |
  |---|---|
  | GPIO5 | Fan rail SSR-40 DD (on when Peltier cooling or heater heating) |
  | GPIO8 | WS2812 RGB LED (built-in DevKitC-1 LED) |
  | GPIO9 | BOOT / page button — OLED page cycle + BLE provisioning authorizer |
  | GPIO10 | Free — claimed by *either* the optional cold-plate DS18B20 (DATA + 4.7 kΩ pull-up) *or* the ST7789 TFT DC line (`docs/display-plan.md`), not both |
  | GPIO18 | Peltier (cooling) SSR-40 DD — `ledc` 15 Hz; driven by the 30 s humidity loop |
  | GPIO19 | Heater SSR-40 DD — `ledc` 15 Hz; `heat_output` of the PID |
  | GPIO21 | I²C SDA (SHT45 + SSD1306) |
  | GPIO22 | I²C SCL (SHT45 + SSD1306) |
  | GPIO23 | Unused (formerly dehumidifier relay) |

- **Shared I²C bus**: the chamber sensor (SHT31/SHT45, address `0x44`) and SSD1306 OLED (address `0x3C`) share GPIO21/GPIO22. Do not add a second `i2c:` block — add new devices to the existing bus with their own `address:` key.
- **Humidity loop drives the Peltier**: the 30 s loop bang-bangs the Peltier (`peltier_output.set_level(1.0/0.0)`) to chase dew point or VPD — cooling the cold plate below the dew point condenses moisture out of the air. The `peltier_cooling` global tracks demand (a float output can't be read back). Whenever the Peltier is commanded on, the fan is turned on in the same lambda (hot-side airflow). Loop priority: frost guard → high-temp ceiling → VPD → Dew Point → off.
- **Cure programs**: The 10-day dry program is driven by `time.homeassistant` cron (midnight). Requires HA time sync. Day counter uses `restore_value: true` — restarting ESPHome does not reset it.
- **10-day dry program**: `dry10_day` counter (0–10). Midnight cron sets `dew_point_setpoint`: day 1 → 13.9 °C (mid-ramp), days 2–5 → 12.2 °C, days 6–9 → 11.1 °C, day ≥10 → auto-off. Program start sets the ramp origin 15.6 °C and temp target 17.2 °C (63 °F). The `dry10_program_status` text sensor exposes progress.
- **Sensor calibration**: SHT45 self-heating is ~0.1–0.2 °C (much less than SHT31). Still calibrate with `offset` in `filters` after install.
- **Dew-point philosophy**: control dew point, not raw RH. With `use_dew_point_control` ON, the Peltier is driven by `dew_point_setpoint` (°C). The `dew_point` sensor is calculated from SHT45 T + RH via Magnus formula — do not replace it with a direct sensor.
- **Humidity control modes**: Dew Point mode is the only user-selectable mode. A VPD mode still exists in the code (`use_vpd_control`, `vpd_setpoint`, `vpd_hysteresis`, the `vpd`/`vpd_error` sensors) but all of it is now `internal: true` — hidden from the web UI and HA, so VPD can't be enabled and the VPD branch in the 30 s loop is dead-but-harmless. The mutual-exclusion (`use_dew_point_control` on_turn_on turns off `use_vpd_control`) is still wired. To bring VPD back, remove the `internal: true` flags (and restore the `web_server` sorting keys + the HA dashboard cards). Both modes drive only the Peltier — no humidifier/dehumidifier relay. RH-only control was removed (RH without temperature is meaningless).
- **ESP32-C6 requires ESP-IDF**: The `framework: type: esp-idf` must not be changed to `arduino`. The C6 variant is not Arduino-compatible in ESPHome.
- **BLE provisioning**: `esp32_improv` is enabled with `authorizer: page_button` (GPIO9 BOOT button). Hold the BOOT button while a phone scans for the device to authorize WiFi provisioning. `improv_serial` provides the same over USB serial.
- **UTF-8 in text-sensor / display lambdas**: non-ASCII glyphs must be emitted as terminated hex byte escapes. Write `°C` as `\xc2\xb0""C`, **not** `\xc2\xb0C` — in the latter the `\x` escape greedily absorbs the following `C` hex digit, producing byte `0x0C` and invalid UTF-8. HA's protobuf parser rejects the malformed `TextSensorStateResponse` and drops the API connection in a reconnect loop (`CONNECTION_CLOSED errno=128`). The `""` terminates the escape. Applies to all `°`, `→` (`\xe2\x86\x92`), and `—` (`\xe2\x80\x94`) glyphs in `chamber_status`, `humidity_control_mode`, `dry10_program_status`, and the OLED page lambdas.
- **WiFi power save is intentionally disabled** (`power_save_mode: none`): ESP-IDF's default modem sleep lets the radio go dormant between DTIM beacons, which some APs (notably Ubiquiti) read as a dead client and evict on a ~15-minute timer — the device flaps offline→online without rebooting. Cost is ~20 mA extra idle current, negligible for a mains-powered controller. Do not remove this line.
- **No preset buttons**: the former "Apply Dry Profile"/"Apply Cure Profile" one-tap buttons were removed in v1.3.1 (redundant with the programs + the always-visible Dew Point Setpoint number, and their 20 °C temp target conflicted with the 17.2 °C default). Manual holds = set the Dew Point Setpoint number directly with Dew Point mode ON. Don't re-add them.
- **Chamber sensor swap (SHT31 ↔ SHT45)**: selected by `substitutions.sht_platform` (`sht3xd` or `sht4x`); **the active default is `sht4x` (SHT45)** with the SHT31 lines kept commented directly below. Both are I²C 0x44, same wiring. The sensor block omits `precision`/`repeatability` and the heater key — both platforms default to highest-quality measurement and heater-off, so a bare block is valid for either. The component `id` stays `sht45` regardless (avoids touching every `id(chamber_temp)`/`id(chamber_rh)` ref). **Swapping = three substitutions** (all at the top of `espcure.yaml`, documented inline): `sht_platform` plus the matching `sht_heater_on`/`sht_heater_off` pair. No lambda editing. CI compiles both variants so a mismatch fails the PR.
- **On-chip heater / Clear Sensor Condensation**: the button's heater statements come from the `sht_heater_on`/`sht_heater_off` substitutions, so one button compiles for either sensor. The **SHT31** (sht3xd) has a real runtime toggle — `set_heater_enabled(bool)` (the driver writes the heater enable/disable I²C command). The **SHT45** (sht4x) has **no on-demand heater API** — its `heater_power`/`heater_time`/`heater_max_duty` are config-time only (applied once at setup; there is no `set_heater_max_duty()` runtime method). So on SHT45 the substitutions are no-ops (`";"`) and the button just refreshes the reading. ⚠️ **`esphome config` does NOT compile lambdas** — a wrong heater method only fails at compile; that's why CI now **compiles both variants** (`.github/workflows/validate.yml` matrix) to catch it.
- **Temp target**: the 10-Day Dry program holds temp target 17.2 °C (63 °F). Dew-point setpoints drive the Peltier.
