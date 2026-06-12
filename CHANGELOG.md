# Changelog

All notable changes to EspCure are documented here.

---

## [Unreleased]

### Added
- **VPD target mode** — third humidity control mode (`VPD Control Mode` switch); `VPD Setpoint` and `VPD Hysteresis` number entities; controls dehumidifier to hit target VPD
- **Optional cold-plate sensor section** (commented YAML): DS18B20 one-wire on GPIO10 for direct frost detection
- **GitHub Actions CI** — `esphome config` validation runs on every PR that touches `espcure.yaml`; `requirements.txt` added
- **HA dashboard enhancements** — VPD gauge, color-coded overview badges, conditional program progress bars, 7-day temperature history, VPD control section
- **Made for ESPHome compliance** — `esp32_improv` and `improv_serial` components added for BLE + serial WiFi provisioning

### Changed
- **README.md** rewritten to reflect current hardware (ESP32-C6, SHT45, SSR-40 DDs) and all current features (OLED, RGB LED, three humidity modes, Cannatrol 4+4, VPD, CI)
- `cannatrol_day` max_value raised 8 → 9 to accommodate end-of-program day counter
- Removed piezo buzzer (`ledc_output`, `rtttl`, frost/program-complete melodies); GPIO10 is now free
- `docs/display-plan.md` rewritten as an "implemented" reference (OLED live in config); updated GPIO budget to reflect GPIO8/9 assignments
- `docs/setup.md` full rewrite: LED colour table, OLED page guide, 10-step setup, comprehensive first-run checklist
- `docs/hardware.md`: buzzer removed from BOM/GPIO table; OLED wiring section added
- `docs/calibration.md`: removed DS18B20 section (no cold-plate sensor in this build); added humidity salt reference table
- `CLAUDE.md`: added OLED and WS2812 RGB LED to capabilities; added display/LED key-section entries

---

## v0.9.0 — 2026-06-11

### Added
- **SSD1306 OLED display** — 3-page cycling (temp/RH/DP/VPD, control settings, program status); 5 s auto-cycle; BOOT button (GPIO9) manual page advance
- **WS2812 RGB LED** (GPIO8, built into DevKitC-1) — cooling=blue, heating=red(dim), idle=green(very dim), frost=white Frost Blink effect
- **`docs/display-plan.md`** — display hardware options, wiring, ESPHome config skeleton, TFT upgrade path

---

## v0.8.0 — 2026-06-10

### Added
- **Rich HA Lovelace dashboard** (`docs/ha-dashboard.yaml`) — 5 tabs: Overview (gauges, history), Programs (cure programs + presets), Outputs (relay states), PID Tuning (live Kp/Ki/Kd sliders + reference), Diagnostics
- `chamber_temp_f` sensor (°F) for Cannatrol-style display

### Changed
- Offline warning card added to Overview tab (conditional on `controller_online`)

---

## v0.7.0 — 2026-06-09

### Added
- **Live PID tuning** — `PID Kp`, `PID Ki`, `PID Kd` number entities; changes apply instantly via `climate.pid.set_control_parameters`; values persist across reboots via `restore_value: true` + `on_boot` priority -200
- **PID Autotune button** — triggers ESPHome relay-feedback autotune
- `docs/pid-tuning.md` — live tuning workflow, autotune procedure, diagnostic reference table

---

## v0.6.0 — 2026-06-08

### Added
- **Device-hosted web UI** (`web_server: version: 3, local: true`) — full React dashboard at `http://espcure.local`; dark mode toggle; works without Home Assistant
- **One-tap presets**: Apply Dry Profile, Apply Cure Profile, Apply Cold-Plate Profile buttons

---

## v0.5.0 — 2026-06-07

### Added
- **Cannatrol 4+4 program** — 4-day dry (12.2 °C DP) → 4-day cure (11.1 °C DP); `cannatrol_phase` global tracks phase; midnight cron advances day counter; `Cannatrol Program Status` text sensor
- **Dew Point Control Mode switch** — toggles between RH bang-bang and dew-point bang-bang
- `Dew Point Setpoint` + `Dew Point Hysteresis` number entities
- `Dew Point Error` diagnostic sensor
- `docs/cure-programs.md` — both programs, presets, HA automation examples

---

## v0.4.0 — 2026-06-06

### Added
- **18-day step-down cure program** — −1 %/day from 78 % → 60 % RH; `Cure Program Day` counter; midnight cron; `Cure Program Status` text sensor
- `Humidity Setpoint` + `Humidity Hysteresis` number entities
- `Humidity Error` diagnostic sensor

---

## v0.3.0 — 2026-06-05

### Added
- **Dew Point** + **VPD** derived sensors (Magnus formula)
- **Chamber Status** text sensor (Cooling / Heating / Idle / Frost Guard)
- **Humidity Control Mode** text sensor (live setpoint readout)
- **Software frost floor** — `min_chamber_temp` number entity; 60 s guard loop; PID suspends/resumes; `Frost Floor Active` binary sensor
- **SHT45 on-chip heater** — `Clear Sensor Condensation` button (logs pulse; `heater_max_duty: 0.0` keeps it off by default)

---

## v0.2.0 — 2026-06-04

### Added
- **PID temperature control** — `climate.pid` with dual `slow_pwm` outputs (Peltier TEC + PTC heater, 20 s period)
- **Fan relay** (GPIO5, SSR-40 DD) — always ON at boot via `on_boot` priority -100
- **Dehumidifier relay** (GPIO23) — 30 s humidity bang-bang loop
- **Min Chamber Temperature** (frost floor) setpoint
- Home Assistant native API (encrypted) + OTA + fallback AP
- `docs/hardware.md`, `docs/setup.md`, `docs/calibration.md`

---

## v0.1.0 — 2026-06-03

### Added
- Initial ESPHome config for **ESP32-C6** (ESP-IDF framework, `variant: esp32c6`)
- **SHT45** sensor (`sht4x` platform, I2C 0x44, `precision: High`)
- I2C bus on GPIO21/22
- WiFi + captive portal + `secrets.yaml` pattern
- `CLAUDE.md` + sub-agent definitions
