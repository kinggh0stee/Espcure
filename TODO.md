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
- [x] Humidifier support — GPIO20 relay, upward RH/DP/VPD control, setpoint entities
- [x] VPD target mode — third control mode (`VPD Control Mode` switch), VPD setpoint/hysteresis entities
- [x] Optional hardware sections in config (door sensor, cold-plate DS18B20, multi-zone SHT45 — commented)
- [x] GitHub Actions CI — `esphome config` validation on PRs (`.github/workflows/validate.yml`)
- [x] Changelog (`CHANGELOG.md`)

---

## 🔴 Before First Flash

These require physical access to the hardware — they can't be done in config alone.

- [ ] **`esphome config espcure.yaml`** — validate zero errors on your machine (CI runs this on PRs, but confirm locally with your secrets)
- [ ] Copy `secrets.yaml.example` → `secrets.yaml`, fill in WiFi credentials + API key + OTA password
- [ ] Verify GPIO pin assignments against your actual DevKit pinout (GPIO5/18/19/20/21/22/23)
- [ ] Confirm SHT45 I2C address — check `esphome config` or boot logs; expected 0x44
- [ ] Calibrate SHT45 temperature + humidity offsets after first flash (`docs/calibration.md`)

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

These require a running device and cannot be done in YAML alone:

- [ ] **Run PID autotune** after first install and update `pid_kp/ki/kd` values + log in `docs/pid-tuning.md`
- [ ] **Calibrate SHT45** — set temp and RH `offset` values in `espcure.yaml` filters
- [ ] **Verify SSR 3.3V trigger** — confirm each SSR-40 DD switches reliably at 3.3 V GPIO level (if not, add 2N2222 NPN driver, see `docs/hardware.md`)
- [ ] **Test dehumidifier + humidifier relays** — confirm GPIO23 and GPIO20 wiring before enabling
- [ ] **Time sync** — verify `time.homeassistant` syncs correctly; cure midnight cron depends on it

---

## 🟡 Home Assistant Dashboard

- [x] **Rich dashboard** — VPD gauge, color-coded badges, conditional program progress cards, 7-day history, VPD control section, humidifier controls (all in `docs/ha-dashboard.yaml`)
- [ ] **Notifications** — HA automation YAML for frost + program complete alerts is in `docs/cure-programs.md`; paste into HA to enable
- [ ] **Energy monitoring** — requires additional hardware (INA219 current sensor on 12 V rail)

---

## 🟢 Features (Future Iterations)

- [x] **Multi-zone support** — optional commented section in `espcure.yaml`; enable second SHT45 at I2C 0x45
- [x] **Door sensor** — optional commented section in `espcure.yaml`; GPIO11 reed switch
- [x] **Humidifier support** — fully implemented (GPIO20, upward RH/DP/VPD control)
- [x] **VPD target mode** — fully implemented (third humidity control mode)
- [x] **Cold-plate sensor** — optional commented section in `espcure.yaml`; DS18B20 one-wire on GPIO10
- [ ] **SD card logging** — local CSV data log without HA dependency (requires SPI SD card module)
- [ ] **HA energy dashboard** — requires INA219 power sensor hardware
- [ ] **Touchscreen display** — ILI9341 2.8" with touch; upgrade path in `docs/display-plan.md`

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
- Humidifier (GPIO20) requires a connected humidifier hardware unit; relay turns on but has no effect without one
- VPD mode controls both dehumidifier and humidifier; do not enable VPD mode without a humidifier connected unless you accept the humidifier relay clicking with no effect
