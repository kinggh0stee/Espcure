# EspCure — Project TODO

Priority: 🔴 Critical · 🟡 High · 🟢 Nice-to-have · ✅ Done

---

## ✅ Completed

- [x] ESP32-C6 + SHT45 ESPHome config (ESP-IDF framework)
- [x] PID temperature control — Peltier (cool) + PTC heater (heat)
- [x] Dual humidity control: RH mode (bang-bang) + Dew Point mode (Cannatrol)
- [x] Dew point + VPD derived sensors
- [x] 18-day step-down cure program (−1 %/day, 78 %→60 %)
- [x] Cannatrol 4+4 built-in program (auto dry→cure phase at midnight)
- [x] One-tap profile presets (Dry, Cure, Cold-Plate)
- [x] Live PID tuning (Kp/Ki/Kd number entities, persist across reboots)
- [x] Software frost floor (no cold-plate sensor required)
- [x] Chamber Status / Humidity Control Mode / Program Status text sensors
- [x] Device-hosted web UI at `http://espcure.local` (web_server v3, dark mode)
- [x] Home Assistant native API (encrypted), all entity metadata
- [x] OTA updates + fallback AP
- [x] Lovelace dashboard YAML (`docs/ha-dashboard.yaml`)
- [x] Full documentation (hardware, setup, calibration, PID tuning, cure programs)
- [x] Sub-agents + CLAUDE.md
- [x] SSD1306 OLED display — 3-page cycling, BOOT button page advance
- [x] WS2812 RGB LED (GPIO8) — PID action color, Frost Blink effect
- [x] Rich HA dashboard — VPD gauge, badges, conditional program cards, progress bars, 7-day history
- [x] VPD target mode — third control mode (`VPD Control Mode` switch), VPD setpoint/hysteresis entities
- [x] Optional cold-plate DS18B20 section (commented YAML, GPIO10)
- [x] GitHub Actions CI — `esphome config` validation on PRs (`.github/workflows/validate.yml`)
- [x] Changelog (`CHANGELOG.md`)

---

## 🔴 Before First Flash

> Config and CI are ready. These are physical deployment steps — follow **`docs/setup.md`**:
> 1. `cp secrets.yaml.example secrets.yaml` and fill in credentials
> 2. `esphome config espcure.yaml` locally with your real secrets
> 3. Verify GPIO5/18/19/21/22/23 against your DevKit pinout
> 4. Confirm SHT45 boots at I2C 0x44 (scan log at first boot)
> 5. Calibrate SHT45 offsets after first flash (`docs/calibration.md`)

---

## 🟡 Hardware Additions

- [x] **Display (SSD1306 OLED)** — config live in `espcure.yaml`; wire VCC/GND/SDA/SCL to GPIO21/22
  - 3 pages: Primary (temp/RH/DP/VPD), Control (setpoints/WiFi), Programs (status/error)
  - BOOT button (GPIO9) cycles pages — no extra wiring
  - Upgrade path to color TFT documented in `docs/display-plan.md`

- [x] **Physical button** — BOOT button (GPIO9) wired as display page-cycle button
  - Cycles OLED display pages; no extra wiring needed

- [x] **Status LED** — built-in WS2812 on GPIO8 (DevKitC-1), 2 s interval
  - Cooling = blue, Heating = red (dim), Idle = green (very dim), Frost = white Frost Blink effect

---

## 🟡 ESPHome Config — Post-Install

> These require a running, installed device. See **`docs/setup.md`** and **`docs/pid-tuning.md`**:
> - Run PID autotune and log results in `docs/pid-tuning.md`
> - Set SHT45 temperature/RH `offset` values in `espcure.yaml` after calibration
> - Verify each SSR-40 DD triggers reliably at 3.3 V (add 2N2222 NPN if marginal — see `docs/hardware.md`)
> - Test dehumidifier relay GPIO23 wiring
> - Verify `time.homeassistant` syncs (required for midnight cure program cron)

---

## 🟡 Home Assistant Dashboard

- [x] **Rich dashboard** — VPD gauge, color-coded badges, conditional program progress cards, 7-day history, VPD control section (all in `docs/ha-dashboard.yaml`)
- [x] **Notifications** — HA automation YAML for frost + program complete alerts documented in `docs/cure-programs.md`; paste into HA to activate
- [ ] **Energy monitoring** — future: requires INA219 current sensor hardware on 12 V rail

---

## 🟢 Features (Future Iterations)

- [x] **VPD target mode** — fully implemented (third humidity control mode, dehumidifier-only)
- [x] **Cold-plate sensor** — optional commented section in `espcure.yaml`; DS18B20 one-wire on GPIO10
- [ ] **SD card logging** — local CSV data log without HA dependency (requires SPI SD card module)
- [ ] **HA energy dashboard** — requires INA219 power sensor hardware
- [ ] **Touchscreen display** — ILI9341 2.8" with touch; upgrade path in `docs/display-plan.md`
- [ ] **Multi-zone second SHT45** — second sensor at I2C 0x45 if needed in future
- [ ] **Humidifier** — upward RH control if ever needed; would add GPIO relay + setpoint entity

---

## 🟢 Documentation

- [ ] Wiring photo guide (reference photos for each SSR connection)
- [ ] Video walkthrough of web UI and HA dashboard
- [x] GitHub Actions CI — `.github/workflows/validate.yml` runs `esphome config` on PRs
- [x] Changelog — `CHANGELOG.md`

---

## Known Limitations

- `web_server` v3 dark mode follows system preference — no server-side force-dark option in ESPHome YAML
- Cure programs require HA time sync (`time.homeassistant`); device must be connected to HA for midnight cron to fire reliably
- Frost protection reacts to chamber *air* temperature (SHT45), not cold-plate surface — may be slow to respond to rapid over-cooling
- SHT45 self-heating (~0.1–0.2 °C) means temperature reads slightly high; calibrate with offset after install
- SSR-40 DD control voltage is at the minimum spec (3.3 V = 3 V min) — verify each SSR before final install
- VPD mode controls only the dehumidifier (downward); there is no humidifier in this build
