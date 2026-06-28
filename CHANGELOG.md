# Changelog

All notable changes to EspCure are documented here.

---

## [Unreleased]

## v1.3.1 — 2026-06-28

### Fixed
- **WiFi link no longer drops every ~15 minutes.** ESP-IDF's default WiFi modem sleep (`WIFI_PS_MIN_MODEM`) let the radio go dormant between DTIM beacons, which some access points (notably Ubiquiti's) read as a dead client and evict on a ~15-minute health-check timer — the device flapped offline→online without ever rebooting (uptime kept climbing). Added `power_save_mode: none` to the `wifi:` block to keep the radio always-on. Trade-off: ~20 mA higher idle current, negligible for a mains-powered controller.
- **OLED page 1 decluttered.** The primary readings page dropped the never-used VPD figure and now shows the dew point alongside its setpoint (`DP 13.5°C  SP 11.1°C`), the dew-point error next to the chamber status, and a context-aware bottom row (frost guard / active program day + temp target / standby). Makes it clear at a glance whether the Peltier needs to run. Pages 2 and 3 are unchanged.

### Removed
- **Apply Dry Profile / Apply Cure Profile preset buttons removed.** The two one-tap presets set a fixed dew-point setpoint, forced the temp target to 20 °C, and enabled dew-point mode. They were redundant — the 10-Day Dry program covers drying and the always-visible **Dew Point Setpoint** number can park the chamber at any hold value by hand — and their 20 °C temp target conflicted with the new 17.2 °C (63 °F) default. To park a manual hold (e.g. a 52 °F / 11.1 °C storage cure), set the Dew Point Setpoint number directly with Dew Point mode ON. Removed from the device web UI, Home Assistant, and the HA dashboard.

### Changed
- **Dew Point Hysteresis default tightened to 0.1 °C** (was 0.5 °C). The Peltier now holds the dew-point band ±0.1 °C instead of ±0.5 °C, tracking the setpoint much more tightly at the cost of more frequent on/off cycling. Adjustable live via the `Dew Point Hysteresis` number. Note: this is `restore_value: true`, so existing units keep their stored value across an update — set it to 0.1 in the web UI (or it applies automatically on a fresh/NVS-cleared install).
- **Default temperature target raised to 17.2 °C (63 °F).** The PID `default_target_temperature` and the 10-Day Dry program's temp target moved from 15.6 °C (60 °F) to 17.2 °C (63 °F), matching the validated real-world program default (heater rarely runs; chamber floats ~63–67 °F). Dew-point setpoints and the 10-day ramp schedule (15.6 → 13.9 → 12.2 → 11.1 °C) are unchanged. The Cannatrol program (20 °C) is unaffected.
- **Default chamber sensor is now the SHT45 (`sht4x`).** The `sht_platform` substitution now ships as `sht4x` (was `sht3xd`/SHT31), with the matching no-op heater substitutions (`sht_heater_on`/`sht_heater_off` = `";"`) since the SHT45 has no on-demand heater API — the Clear Sensor Condensation button just takes a fresh reading. The SHT31 (`sht3xd`) remains a supported option, kept commented inline directly below the active lines for a one-step swap-back. Both variants still compile in CI. Re-calibrate after swapping (see `docs/calibration.md`).

### Added
- **Firmware Version diagnostic sensor** — a new `Firmware Version` text sensor (Diagnostics group, top) shows the running firmware version (e.g. `1.2.0`) on the device web UI and in Home Assistant, so you can confirm what's flashed without reading boot logs. The version now comes from a single `fw_version` substitution that feeds both `esphome.project.version` and this sensor — bump it in one place per release.

## v1.2.0 — 2026-06-20

### Added
- **Renameable device — run multiple EspCures on one network/HA.** The device name and friendly name are now `device_name`/`friendly_name` substitutions at the top of `espcure.yaml` instead of being hardcoded. Set them per unit before flashing to give each its own mDNS hostname (`http://<device_name>.local`), Home Assistant entity-ID prefix, and setup-AP SSID (`<friendly_name>-Setup`), so two or more controllers no longer collide on `espcure.local` or duplicate entity IDs. Defaults are unchanged (`espcure` / `EspCure`). The firmware `project.name` (`kinggh0stee.espcure`) intentionally stays constant across units.
- **Optional MAC-suffix auto-naming** — a `mac_suffix` substitution (default `"false"`) wires `esphome.name_add_mac_suffix`. Set it to `"true"` to append the device MAC to the hostname (`espcure-a1b2c3.local`) so every flashed unit is unique with no per-unit editing — useful for flashing a batch from one config. Trade-off: the clean `<device_name>.local` address is replaced by the MAC-suffixed one (or use the IP).

### Changed
- **Fans now run continuously while a cure program is active.** Previously the fan rail (GPIO5) was ON only when the Peltier was cooling or the heater was heating. Now, whenever a cure program (`10-Day Dry` or `Cannatrol 4+4`) is running, the fans run continuously for constant air circulation and even drying; with no program active the original behaviour (ON when cooling or heating) is unchanged. The Peltier hot-side airflow guarantee is preserved — the fan is still commanded ON in the same lambda as the Peltier.

## v1.1.0 — 2026-06-17

### Fixed
- **Status LED behaviour — purple idle, no more flicker, instant reliable toggle.** Three fixes: (1) the idle colour was green at **0.04** brightness — WS2812s flicker badly at that low a duty cycle, which read as a "pulsing green" LED; idle is now **purple at 0.5** (half power), eliminating the flicker. (2) Toggling felt broken — the painter was edge-triggered inside the 2 s interval, so the `Status LED Enable` switch only took effect on the next tick, and the separate `Status LED` light entity fought the loop (turning it off left nothing to re-assert, so it "toggled off and not on"). The painter is now a shared `paint_status_led` script that the enable switch calls **instantly** on toggle, and the `status_led` light is `internal: true` so the enable switch is the **single** on/off control. (3) On/off now retains across reboots via the enable switch (`RESTORE_DEFAULT_ON`).
- **SHT45 sensor swap no longer breaks the build** — the "Clear Sensor Condensation" button shipped a commented SHT45 block that called `id(sht45).set_heater_max_duty(1.0f)`, but **that method does not exist** on the `sht4x` platform (its heater is config-time only — `heater_power`/`heater_time`/`heater_max_duty` YAML keys; there is no runtime on-demand heater action). Following the documented "swap to SHT45" steps would therefore fail at compile. The button is now driven by `sht_heater_on`/`sht_heater_off` substitutions: a real `set_heater_enabled()` pulse on the SHT31, and no-ops (`";"`, just a fresh reading) on the SHT45. Swapping sensors is now three grouped substitutions with no lambda edits, and CI compiles both variants so a regression can't slip through. (Supersedes the earlier "carries both heater-API variants" note.)
- **Status LED now toggles reliably** — the 2 s status-LED loop previously re-issued a full light call every cycle. That restarted the "Frost Blink" pulse effect each pass (so it never blinked smoothly), mixed `set_transition_length()` with `set_effect()` in the same call (ESPHome drops the transition), and stomped any manual control of the `Status LED` entity within 2 s — so toggling it from HA/the web UI appeared to do nothing. The loop is now **edge-triggered** via a new `led_state` global: it only issues a light call when the cooling/heating/idle/frost state actually changes. Fan control still runs unconditionally every 2 s.
- **PID autotune `negative_output` on heat-only loop** — the autotune button previously used `negative_output: -1.0`, but the temperature PID has no `cool_output`. With no cooling actuator the `-1.0` level goes nowhere, making the relay-feedback oscillation asymmetric and the resulting gains unreliable. Changed to `negative_output: 0.0` so the test correctly oscillates between "heater full on" and "heater off (passive cool-down)". Updated `docs/pid-tuning.md` with heat-only timing expectations (60–120 min) and a recommendation to prefer manual tuning.
- **Text-sensor states crashing the Home Assistant API connection** — the `°C` glyph in several status strings was written as `\xc2\xb0C`, where C's `\x` escape greedily absorbs the following hex-digit `C`, producing the byte `0x0C` and invalid UTF-8 on the wire. HA's protobuf parser rejected the malformed `TextSensorStateResponse`, throwing a fatal `data_received()` error that dropped and reconnected the API connection in a loop (logged on the device as `CONNECTION_CLOSED errno=128`). Terminated each affected escape with `""` (`\xc2\xb0""C`) — the same workaround used for the arrow/em-dash glyphs. Affected the `Humidity Control Mode`, `10-Day Program Status`, and `Cannatrol Program Status` text sensors, plus two OLED display strings. Display-only; no behavior change beyond a stable HA connection.

### Added
- **Status LED is now a cure-progress indicator.** At half power throughout: **purple** when idle (no program), then while a cure program runs it fades **blue → green** as the days advance (`rgb(0, day/total, 1−day/total)` — blue on day 0, greener each day; `total` = 10 for the 10-Day Dry program, 8 for Cannatrol 4+4), and holds **solid green ("cured")** after the program auto-completes, via a new restored `cure_complete` global (cleared when the next program starts). Frost guard still overrides with a white blink. The day-counter `on_value` and the program switches repaint instantly. This replaces the previous cooling=blue / heating=red operational colors on the LED.
- **Status LED Enable switch** — a new `Status LED Enable` switch (Status & Indicators group, default ON) gates the automatic status-LED indicator. Turn it off to kill the WS2812 glow entirely (e.g. in a dark room); the 2 s loop turns the LED off and stops driving it until re-enabled. Fan control is unaffected — it always runs. Pairs with the edge-trigger fix: with the LED enabled, status indication stays automatic; toggling the LED light entity directly is still respected until the next state change.
- **CI now compiles both sensor variants** — `.github/workflows/validate.yml` gained a matrix `compile` job that builds the firmware for **both** `sht_platform` values (SHT31 and SHT45) after the `esphome config` step, with the PlatformIO/ESP-IDF toolchain cached. `esphome config` only parses YAML — it does **not** compile lambdas — so enum/method typos (like a wrong sensor-heater call) previously slipped through to flash time. The compile gate catches them, and keeps either sensor option buildable.
- **Selectable chamber sensor (SHT31 or SHT45)** — added a `sht_platform` substitution at the top of `espcure.yaml` to switch between the SHT31 (`sht3xd`) and SHT45 (`sht4x`). Both share I²C 0x44 and the same wiring; only the platform and the on-chip heater API differ. The sensor block now omits `precision`/`heater_max_duty` (both platforms default to highest-quality measurement + heater-off). The "Clear Sensor Condensation" button's heater statements come from the `sht_heater_on`/`sht_heater_off` substitutions, set alongside `sht_platform` (see the SHT45 swap fix below). Default ships as `sht3xd` (SHT31). Docs: `docs/hardware.md` "Swapping the chamber sensor" + `docs/calibration.md` re-calibration note.
- **Clear Sensor Condensation button now works** — the button previously only logged a message. It now pulses the sensor's on-chip heater for one measurement cycle to evaporate condensation, then takes a clean reading. Added `id: sht45` to the sensor platform block to enable on-demand component calls.
- **Cross-platform setup instructions** — `README.md` and `docs/setup.md` now give both Linux/macOS and Windows (PowerShell) commands for creating a venv, installing the pinned ESPHome, copying `secrets.yaml`, and generating the API key. `CLAUDE.md` notes the Windows `py -m esphome` / `Copy-Item` equivalents.

- **Firmware version reporting** — the device now declares its version via ESPHome `project` (`kinggh0stee.espcure` / `1.1.0`), shown in the boot logs and Home Assistant device info. Bump on each tagged release.

### Changed
- **Device web UI declutter** — the `espcure.local` page was reorganized and thinned. Key correction: in `web_server` v3, `entity_category: config`/`diagnostic` does **not** hide entities from the device web page (it only tucks them away in Home Assistant), and sorting groups render expanded on load — so the live page previously listed everything. New scheme: six groups (Climate & Temperature, Humidity & Dew Point, Cure Programs, **Status & Indicators**, **Setup & Tuning**, Diagnostics) with essentials on top; every `entity_category: config` knob (frost floor, safety ceiling, dew-point hysteresis, PID Kp/Ki/Kd, autotune, day counters, Clear Sensor Condensation) now clusters in the bottom "Setup & Tuning" group, and diagnostics sit last. `Frost Floor Active` (live safety flag) is promoted near the top; `Controller Online` and `Restart Controller` gained `entity_category: diagnostic` (HA tidiness). No control/safety logic changed; fully reversible.
- **Web UI reorganization** (`web_server` v3 sorting groups):
  - **6 groups instead of 7** — merged the thin VPD group into "Humidity & Dehumidification" (VPD and Dew Point are two modes of one loop, so all four VPD entities now sit beside their Dew Point counterparts).
  - **Set-once knobs hidden via `entity_category: config`** — PID Kp/Ki/Kd, PID Autotune, the dew-point/VPD hysteresis, frost floor + safety ceiling, the program day counters, and Clear Sensor Condensation now live in the config section instead of cluttering the live dashboard.
  - **Climate renamed "Chamber Temperature" → "Temperature Control"** to end the name collision with the `chamber_temp` sensor (also renames the HA entity to `climate.espcure_temperature_control`).
  - **"Peltier Output" → "Peltier (Dehumidify) Duty"**, moved to Diagnostics with `entity_category: diagnostic` (renames HA entity to `sensor.espcure_peltier_dehumidify_duty`).
  - **Reordered** — Apply Dry/Cure presets promoted to the top of Cure Programs; Frost Floor Active promoted to the top of Diagnostics.
  - **`Chamber Fans`** marked `diagnostic` (it is auto-driven by the 2 s loop; manual toggling fights the controller).
  - `docs/ha-dashboard.yaml` updated for the two renamed entity_ids.
- **Docs sweep / accuracy pass** across every document:
  - `docs/setup.md` now installs ESPHome via the pinned `requirements.txt` (was bare `pip install esphome`), matching CI.
  - `docs/cure-programs.md` corrected the VPD Hysteresis default to **0.1 kPa** (config value; doc previously said 0.2) and added the 0.8 kPa VPD Setpoint default.
  - `docs/hardware.md` removed a stale "dehumidifier exhaust" mention (no dehumidifier in this build) and fixed the fusing example to match the 300 W / 25 A BOM PSU.
  - `docs/pid-tuning.md` documents the heat-only autotune caveat (`negative_output: -1.0` with no `cool_output`).
  - `docs/display-plan.md` / `CLAUDE.md` flag that GPIO10 is claimed by *either* the optional cold-plate DS18B20 *or* the ST7789 TFT DC line, not both.
  - `CLAUDE.md` updated for the grouped web UI (`web_server` sorting groups), the UTF-8 byte-escape convention, diagnostic sensors, and per-program temp targets.

### Removed
- **VPD mode + two helper entities hidden from the UI (web page + HA) via `internal: true`** — to declutter, the entire VPD suite (`vpd` sensor, `vpd_error`, `vpd_setpoint`, `vpd_hysteresis`, `use_vpd_control`), the `page_button` BOOT-button binary sensor, and the duplicate `humidity_control_mode` text sensor are now `internal: true`. They keep working internally (the OLED still reads `vpd`/`humidity_control_mode`; the BOOT button still cycles OLED pages and authorizes BLE provisioning; the dew-point mutual-exclusion still fires) but no longer appear on the device web page or in Home Assistant. Dew Point is now the only user-selectable humidity mode; the 30 s VPD branch is dead-but-harmless. `docs/ha-dashboard.yaml` had its VPD gauge, VPD history line, Humidity-Control-Mode badge/row, VPD Control Mode card, and VPD Error diagnostic line removed accordingly. Reversible by deleting the `internal: true` flags (and restoring the web/HA references).
- **Fahrenheit, entirely — the build is now Celsius-only.** Removed the `chamber_temp_f` and `dew_point_f` °F template sensors, the OLED's °F temperature/setpoint readouts, and every °F reference from the web UI, the HA dashboard (`docs/ha-dashboard.yaml`), and the documentation. The OLED main page now shows the temperature setpoint in the slot the °F readout used to occupy. Numeric temperatures are reported in °C only. (A `Fahrenheit Display` toggle was prototyped and then dropped in favor of Celsius-only.)

---

## v1.0.0 — 2026-06-13

First stable release. Major control-loop rework plus a full documentation and UI polish pass.

### Added
- **Control-topology rework** — the Peltier now chases dew point / VPD (cold-plate condensation is the dehumidifier) and the heater chases temperature. The temperature PID is now **heat-only**.
- **10-Day Dry Program** (`10-Day Dry Program` switch) — dew-point recipe: a 2-day ramp 60→57→54 °F DP, hold 54 °F (days 3–6), hold 52 °F (days 7–10), auto-off after day 10. `10-Day Program Day` counter and `10-Day Program Status` text sensor.
- **High-temperature safety ceiling** — `Max Chamber Temperature (Safety Ceiling)` number (default 27 °C / 80 °F). Because the PID is heat-only, this forces the Peltier on above the ceiling so the chamber can't overheat.
- **VPD target mode** — humidity control mode (`VPD Control Mode` switch); `VPD Setpoint` and `VPD Hysteresis` number entities
- **Organized web UI** — entities grouped (Climate & Temperature, Humidity & Dew Point, VPD, Cure Programs, PID Tuning, Hardware & Status, Diagnostics) via `web_server` v3 sorting groups, plus added icons across the board.
- **Peltier Output** and **VPD Error** sensors — exposed so the Home Assistant dashboard renders without missing entities.
- **Docs site polish** — SVG favicon, `display-plan.md` added to the MkDocs nav.
- **Optional cold-plate sensor section** (commented YAML): DS18B20 one-wire on GPIO10 for direct frost detection
- **GitHub Actions CI** — `esphome config` validation runs on every PR that touches `espcure.yaml`; `requirements.txt` added
- **HA dashboard enhancements** — VPD gauge, color-coded overview badges, conditional program progress bars, 7-day temperature history, VPD control section
- **Made for ESPHome compliance** — `esp32_improv` and `improv_serial` components added for BLE + serial WiFi provisioning

### Changed
- **Temperature PID is now heat-only** (`cool_output` removed). Default target raised 55 °F → **60 °F (15.6 °C)** — a realistic floor for Peltier strength. Set to `mode: HEAT` on boot.
- **Peltier is no longer a PID output** — it is bang-bang driven by the 30 s dew-point/VPD loop via `set_level(1.0/0.0)`. New `peltier_cooling` global tracks demand.
- **Frost guard** now forces the **Peltier** off below `min_chamber_temp` (was: suspend whole PID). The heater keeps running during frost to aid recovery.
- **Fan relay** ON when the Peltier is cooling OR the heater is heating; commanded ON in the same lambda as the Peltier so the hot-side fan always has airflow.
- **Peltier and heater outputs** both use `ledc` at 15 Hz (Peltier switched from `slow_pwm`; junction sees average power, reducing fatigue).
- **BOM**: replaced 5 V PSU with a 12 V → 5 V buck converter (e.g. LM2596 or MP1584EN module) — one less power brick.
- **README.md** rewritten to reflect current hardware (ESP32-C6, SHT45, SSR-40 DDs) and current features (OLED, RGB LED, two humidity modes, Cannatrol 4+4 + 10-Day Dry, VPD, CI)
- `cannatrol_day` max_value raised 8 → 9 to accommodate end-of-program day counter
- Removed piezo buzzer (`ledc_output`, `rtttl`, frost/program-complete melodies); GPIO10 is now free
- `docs/display-plan.md` rewritten as an "implemented" reference (OLED live in config); updated GPIO budget to reflect GPIO8/9 assignments
- `docs/setup.md` full rewrite: LED colour table, OLED page guide, 10-step setup, comprehensive first-run checklist
- `docs/hardware.md`: buzzer removed from BOM/GPIO table; OLED wiring section added
- `docs/calibration.md`: removed DS18B20 section (no cold-plate sensor in this build); added humidity salt reference table
- `CLAUDE.md`: added OLED and WS2812 RGB LED to capabilities; added display/LED key-section entries
- `docs/hardware.md`, `docs/cure-programs.md`, `docs/pid-tuning.md`, `docs/ha-dashboard.yaml`, `CLAUDE.md`: updated for the heat-only / Peltier-dehumidification topology, the new 10-Day Dry program, and the safety ceiling

### Removed
- **External dehumidifier relay** (`Dehumidifier` switch, GPIO23) — the Peltier cold plate is now the sole dehumidification mechanism. GPIO23 is free.
- **RH humidity control mode** — `Humidity Setpoint` / `Humidity Hysteresis` numbers, the `Humidity Error` sensor, and the RH bang-bang branch. RH without temperature is unreliable.
- **18-day RH step-down program** — `Cure Program (18-day)` switch, `Cure Program Day` counter, `Cure Program Status` sensor (replaced by the 10-Day Dry program).
- **Apply Cold-Plate Profile** button — it relied on the removed RH fallback.
- **PID Cool Output** diagnostic sensor — the PID no longer has a cool output.

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
