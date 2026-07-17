# EspCure — Project TODO

Priority: 🔴 Critical · 🟡 High · 🟢 Nice-to-have · ✅ Done

---

## ✅ Completed

- [x] ESP32-C6 + SHT45 ESPHome config (ESP-IDF framework)
- [x] Heat-only PID temperature control — PTC heater chases temp (default 17.2 °C / 63 °F)
- [x] Peltier-chases-dew-point topology — TEC drives cold-plate condensation
- [x] Dew Point humidity control mode (VPD hidden/internal)
- [x] Dew point + VPD derived sensors
- [x] 10-Day Dry dew-point program (ramp 15.6→12.2 °C, then 12.2, then 11.1)
- [x] High-temp safety ceiling (`max_chamber_temp`, default 27 °C)
- [x] Live PID tuning (Kp/Ki/Kd number entities, persist across reboots)
- [x] Software frost floor (no cold-plate sensor required; forces Peltier off)
- [x] Chamber Status / Humidity Control Mode / Program Status text sensors
- [x] Device-hosted web UI at `http://espcure.local` (web_server v3, dark mode)
- [x] Home Assistant native API (encrypted), all entity metadata
- [x] OTA updates + fallback AP
- [x] Lovelace dashboard YAML (`docs/ha-dashboard.yaml`)
- [x] Full documentation (hardware, setup, calibration, PID tuning, cure programs)
- [x] Sub-agents + CLAUDE.md
- [x] SSD1306 OLED display — 3-page cycling, BOOT button page advance
- [x] WS2812 RGB LED (GPIO8) — cure-progress indicator, Frost Blink effect, Status LED Enable switch
- [x] Rich HA dashboard — badges, conditional program cards, progress bars, 7-day history
- [x] VPD target mode implemented, then hidden (`internal: true`) — Dew Point is the only user-selectable mode as of v1.1.0
- [x] Optional cold-plate DS18B20 section (commented YAML, GPIO10)
- [x] GitHub Actions CI — `esphome config` validation on PRs (`.github/workflows/validate.yml`)
- [x] Changelog (`CHANGELOG.md`)

### v1.5.0 Shipped (Unreleased)

- [x] **Allende self-tuning cooling loop** — Peltier dew-point control replaced the 30 s bang-bang hysteresis loop with a 20 s proportional + adaptive-bias controller (continuous 0–100% duty, learned steady-state bias, "satisfied cutoff" safety refinement). New `Cool Gain`/`Cool Bias`/`Reset Cool Bias` entities; `Dew Point Hysteresis` repurposed as `Dew Point Deadband`. See `docs/cooling-loop.md`.
- [x] **Cannatrol 4+4 program removed** — 10-Day Dry is now the only built-in cure program.

### v1.1.0 Shipped

- [x] Cure-progress status LED — purple idle, blue→green by day, solid green cured, white blink frost guard
- [x] Status LED Enable switch (single on/off control)
- [x] Selectable chamber sensor (SHT31/SHT45 via `sht_platform` substitution)
- [x] CI matrix compile (both sensor variants validated on PRs)
- [x] Clear Sensor Condensation button (real heater call on SHT31, no-op refresh on SHT45)
- [x] Firmware version reporting (device info + boot logs)
- [x] Web UI declutter (6 sorting groups; VPD + Humidity Control Mode hidden)
- [x] Dew Point as only user-selectable humidity mode (VPD internal/hidden)
- [x] Celsius-only (Fahrenheit removed)
- [x] SHT sensor wiring diagram in docs

---

## 🟢 First-Flash Checklist (reference, per new unit)

> The project itself is well past first flash (see CHANGELOG for release history) — this is reference guidance for anyone building a *new* EspCure unit. Full walkthrough: **`docs/setup.md`**:
> 1. `cp secrets.yaml.example secrets.yaml` and fill in credentials
> 2. `esphome config espcure.yaml` locally with your real secrets
> 3. Verify GPIO5/18/19/21/22/23 against your DevKit pinout
> 4. Confirm SHT45 boots at I2C 0x44 (scan log at first boot)
> 5. Calibrate SHT45 offsets after first flash (`docs/calibration.md`)

---

## 🟡 Hardware Additions

- [x] **Display (SSD1306 OLED)** — config live in `espcure.yaml`; wire VCC/GND/SDA/SCL to GPIO21/22
  - 3 pages: Primary (temp/RH/dew point vs setpoint/status), Control (setpoints/WiFi), Program status (no VPD shown)
  - BOOT button (GPIO9) cycles pages — no extra wiring
  - Upgrade path to color TFT documented in `docs/display-plan.md`

- [x] **Physical button** — BOOT button (GPIO9) wired as display page-cycle button
  - Cycles OLED display pages; no extra wiring needed

- [x] **Status LED** — built-in WS2812 on GPIO8 (DevKitC-1), cure-progress indicator at 50% brightness
  - Idle = purple, Active program = blue→green by day, Cured = solid green, Frost = white blink (safety override)

---

## 🟡 ESPHome Config — Post-Install

> These require a running, installed device. See **`docs/setup.md`** and **`docs/pid-tuning.md`**:
> - Run PID autotune and log results in `docs/pid-tuning.md`
> - Set SHT45 temperature/RH `offset` values in `espcure.yaml` after calibration
> - ~~Verify each SSR-40 DD triggers reliably at 3.3 V~~ ✅ **verified on the reference unit (2026-07)** — all three SSRs trigger reliably at 3.3 V, no NPN driver needed. Still re-verify on any new build (see `docs/hardware.md`)
> - Confirm the hot-side fan energizes the instant the Peltier turns on (shared fan rail)
> - Verify a time source syncs — HA time preferred, SNTP fallback (drives the epoch-anchored cure-program day advancement)

---

## 🟡 Home Assistant Dashboard

- [x] **Rich dashboard** — colour-coded badges, conditional program progress cards, 7-day history (all in `docs/ha-dashboard.yaml`)
- [x] **Notifications** — HA automation YAML for frost + program complete alerts documented in `docs/cure-programs.md`; paste into HA to activate
- [ ] **Energy monitoring** — future: requires INA219 current sensor hardware on 12 V rail

---

## 🟢 Features (Future Iterations)

- [x] **VPD target mode** — fully implemented (humidity control mode; drives the Peltier), later hidden (`internal: true`)
- [x] **Peltier-chases-dew-point topology** — heat-only PID + self-tuning Allende Peltier dehumidification + safety ceiling
- [x] **Cold-plate sensor** — optional commented section in `espcure.yaml`; DS18B20 one-wire on GPIO10
- [ ] **SD card logging** — local CSV data log without HA dependency (requires SPI SD card module)
- [ ] **HA energy dashboard** — requires INA219 power sensor hardware
- [ ] **Touchscreen display** — ILI9341 2.8" with touch; upgrade path in `docs/display-plan.md`
- [ ] **Multi-zone second SHT45** — second sensor at I2C 0x45 if needed in future
- [ ] **Humidifier** — upward RH control if ever needed; would add GPIO relay + setpoint entity

---

## 🟡 Known Bugs / Cleanups

- [x] **Clear Sensor Condensation button** — implemented: `set_heater_max_duty(1.0f)` → `component.update` → `delay 1500ms` → `set_heater_max_duty(0.0f)` → `component.update`. Needs `esphome config` validation before first flash.
- [x] **PID autotune on a heat-only loop** — changed `negative_output: -1.0` → `0.0` so the relay test oscillates between heater full-on and heater off, matching production reality. Updated `docs/pid-tuning.md` with heat-only timing expectations and a preference for manual tuning.

---

## 🟢 Documentation

- [ ] Wiring photo guide (reference photos for each SSR connection)
- [ ] Video walkthrough of web UI and HA dashboard
- [x] GitHub Actions CI — `.github/workflows/validate.yml` runs `esphome config` on PRs
- [x] Changelog — `CHANGELOG.md`
- [x] Windows + Linux/macOS setup instructions (`README.md`, `docs/setup.md`)

---

## Known Limitations

- `web_server` v3 dark mode follows system preference — no server-side force-dark option in ESPHome YAML
- Cure programs prefer HA time sync but self-heal with SNTP fallback — day advancement runs every 60 s and catches up if rebooted or disconnected (no lost days like the old midnight-cron model)
- Frost protection reacts to chamber *air* temperature (SHT45), not cold-plate surface — may be slow to respond to rapid over-cooling
- Dry floor (RH safety) has a 3% release hysteresis (e.g. trip below 55%, release above 58%) to prevent chatter when RH oscillates near the floor
- SHT45 self-heating (~0.1–0.2 °C) means temperature reads slightly high; calibrate with offset after install
- SSR-40 DD control voltage is at the minimum spec (3.3 V = 3 V min) — verified reliable on the reference unit; still verify each SSR on any new build before final install
- Humidity control is downward-only (Peltier condensation); there is no humidifier in this build
- Temperature has no active cooling (heat-only PID) — the chamber floats (typically ~17–19 °C); the `max_chamber_temp` ceiling is the only forced-cooling path
