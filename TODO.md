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

---

## 🔴 Before First Flash

- [ ] **`esphome config espcure.yaml`** — validate zero errors on real machine
- [ ] Copy `secrets.yaml.example` → `secrets.yaml`, fill in all values
- [ ] Verify GPIO pin assignments against your actual DevKit pinout
- [ ] Confirm SHT45 I2C address (scan: `esphome config` logs it at first boot)
- [ ] Calibrate SHT45 temperature + humidity offsets after first flash (`docs/calibration.md`)

---

## 🟡 Hardware Additions

- [x] **Display (SSD1306 OLED)** — config live in `espcure.yaml`; wire VCC/GND/SDA/SCL to GPIO21/22
  - 3 pages: Primary (temp/RH/DP/VPD), Control (setpoints/WiFi), Programs (status/error)
  - BOOT button (GPIO9) cycles pages — no extra wiring
  - Upgrade path to color TFT documented in `docs/display-plan.md`

- [x] **Physical button** — BOOT button (GPIO9) wired as display page-cycle button
  - Acknowledge frost alert
  - Toggle fans on/off
  - Suggested: 1–3× momentary buttons on spare GPIOs

- [ ] **Piezo buzzer** — alert on frost floor activation, program completion
  - Suggested: passive piezo on GPIO with `rtttl` ESPHome component

- [ ] **Status LED** — RGB or single color for quick status at a glance
  - Cooling = blue blink, heating = red blink, idle = green solid, frost = white flash
  - ESP32-C6 DevKitC-1 has a built-in WS2812 RGB LED (GPIO8)

---

## 🟡 ESPHome Config

- [ ] **Run PID autotune** after first install and update `pid_kp/ki/kd` values + log in `docs/pid-tuning.md`
- [ ] **Calibrate SHT45** — set temp and RH `offset` values in `espcure.yaml` filters
- [ ] **Verify SSR 3.3V trigger** — confirm each SSR-40 DD switches reliably at 3.3 V GPIO level (if not, add 2N2222 NPN driver, see `docs/hardware.md`)
- [ ] **Test dehumidifier relay** — confirm GPIO23 wiring before enabling `dehumidifier_relay`
- [ ] **Time sync** — verify `time.homeassistant` syncs correctly; cure midnight cron depends on it
- [ ] Consider `deep_sleep` integration if running on battery backup (optional)

---

## 🟡 Home Assistant Dashboard

- [ ] **Rich dashboard** — expand `docs/ha-dashboard.yaml` with:
  - Real-time gauges for temp, RH, dew point, VPD
  - History graph cards (24 h / 7 day toggle)
  - Conditional cards (only show active program controls)
  - Color-coded status badges
  - Program progress bar (custom:bar-card or progress indicator)
  - Mobile-optimized layout
- [ ] **Notifications** — enable HA automations from `docs/cure-programs.md` for frost + program complete alerts
- [ ] **Energy monitoring** — add PSU current sensor if desired (requires additional hardware: INA219 module)

---

## 🟢 Features (Future Iterations)

- [ ] **Multi-zone support** — second SHT45 in a different chamber area (I2C address 0x45)
- [ ] **Door sensor** — magnetic reed switch on GPIO to log door-open events
- [ ] **Humidifier support** — add humidifier relay + upward RH control for overly dry conditions
- [ ] **VPD target mode** — bang-bang control directly on VPD (useful for active-growth phases)
- [ ] **Cold-plate sensor** — DS18B20 one-wire on a spare GPIO for direct frost detection
- [ ] **SD card logging** — local CSV data log without HA dependency
- [ ] **HA energy dashboard** — wire to HA Energy tab via power sensor
- [ ] **Touchscreen display** — ILI9341 2.8" with touch for full on-device UI

---

## 🟢 Documentation

- [ ] Wiring photo guide (reference photos for each SSR connection)
- [ ] Video walkthrough of web UI and HA dashboard
- [ ] GitHub Actions CI — `esphome config` check on PRs (requires hosted runner with ESPHome installed)
- [ ] Changelog / release notes

---

## Known Limitations

- `web_server` v3 dark mode follows system preference — no server-side force-dark option in ESPHome YAML
- Cure programs require HA time sync (`time.homeassistant`); device must be connected to HA for midnight cron to fire reliably
- Frost protection reacts to chamber *air* temperature (SHT45), not cold-plate surface — may be slow to respond to rapid over-cooling
- SHT45 self-heating (~0.1–0.2 °C) means temperature reads slightly high; calibrate with offset after install
- SSR-40 DD control voltage is at the minimum spec (3.3 V = 3 V min) — verify each SSR before final install
