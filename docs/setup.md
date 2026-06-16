# Setup Guide

## Prerequisites

- Python 3.11+ and ESPHome installed (see below — use the pinned `requirements.txt`)
- Home Assistant running (for HA API integration and time sync)
- Hardware assembled per `docs/hardware.md`
- USB connection to the ESP32-C6 (first flash only)
- Internet access at compile time (Roboto font downloaded from Google Fonts for the OLED display)

### Install ESPHome

Use the pinned `requirements.txt` so your local build matches CI (`esphome==2026.5.3`). A virtual environment keeps it isolated.

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> If `esphome` isn't found after install on Windows, invoke it as `py -m esphome` instead.

---

## 1. Prepare secrets

**Linux / macOS:**
```bash
cp secrets.yaml.example secrets.yaml
```

**Windows (PowerShell):**
```powershell
Copy-Item secrets.yaml.example secrets.yaml
```

Edit `secrets.yaml` with your values:

```yaml
wifi_ssid: "YourNetworkName"
wifi_password: "YourWiFiPassword"
ap_password: "espcure-setup"
api_encryption_key: "<generate below>"
ota_password: "<choose a strong password>"
```

Generate a random API encryption key:

**macOS / Linux:**
```bash
python3 -c "import base64,os; print(base64.b64encode(os.urandom(32)).decode())"
```

**Windows (PowerShell):**
```powershell
[Convert]::ToBase64String((1..32 | ForEach-Object { [byte](Get-Random -Max 256) }))
```

Or if Python is installed on Windows:
```powershell
python -c "import base64,os; print(base64.b64encode(os.urandom(32)).decode())"
```

---

## 2. Validate config

```bash
esphome config espcure.yaml
```

Fix any reported errors before flashing. This also downloads the Roboto font files on first run.

---

## 3. First flash (USB)

Connect the ESP32-C6 DevKit via USB-C. If the device doesn't enter flash mode automatically, hold the **BOOT** button (GPIO9) while pressing **RST**, then release RST.

```bash
esphome run espcure.yaml
```

When complete, the ESP32 reboots and connects to your WiFi. The built-in RGB LED (GPIO8) will show:

| LED color | Meaning |
|---|---|
| Blue | Cooling (Peltier active) |
| Red (dim) | Heating (PTC heater active) |
| Green (very dim) | Idle — PID active but no output |
| White blinking | **Frost guard active** — PID suspended |
| Off | Climate off / booting |

---

## 4. Open the device web UI

Browse to **`http://espcure.local`** (or the IP address shown in ESPHome logs).

The device-hosted dashboard gives full control without Home Assistant:

| Section | What you get |
|---|---|
| **Sensors** | Chamber temp (°C + °F), RH, dew point, VPD, error diagnostics |
| **Climate** | PID thermostat card — adjust target temp, see action state |
| **Controls** | Cure programs, fan, dew-point/VPD mode toggle |
| **Presets** | Apply Dry / Cure profile in one tap |
| **PID Tuning** | Kp/Ki/Kd sliders — changes apply instantly, no reflash |
| **Status** | Chamber Status, Humidity Control Mode, program progress |
| **Dark mode** | Toggle in the top-right corner (follows system preference by default) |

The web UI runs entirely from the ESP32 flash — no internet required after first compile.

---

## 5. OLED display

If you wired an SSD1306 OLED to GPIO21/22 (see `docs/display-plan.md`), it auto-starts and cycles between three pages every 5 seconds:

| Page | Content |
|---|---|
| **Main** | Temperature °C + RH % (large), dew point, VPD, chamber status, temp °F, frost banner |
| **Control** | Humidity control mode, temp setpoint (°C + °F), frost floor, WiFi signal |
| **Programs** | 10-Day Dry + Cannatrol 4+4 status, active humidity/DP error |

Press the **BOOT button** (GPIO9, on the DevKit board) to manually cycle pages.

---

## 6. Add to Home Assistant

1. **Settings → Devices & Services → Add Integration → ESPHome**
2. Enter `espcure.local` (or IP address)
3. Enter the `api_encryption_key` from your `secrets.yaml`
4. All entities appear under the **EspCure** device

### Import the dashboard

A complete 5-tab Lovelace dashboard is at `docs/ha-dashboard.yaml`.

1. **Settings → Dashboards → Add Dashboard**
2. Give it a name (e.g. "EspCure"), toggle **Show in sidebar**
3. Open the new dashboard, click the **⋮ menu → Edit → Raw configuration editor**
4. Paste the contents of `docs/ha-dashboard.yaml` and save

---

## 7. First-run checklist

- [ ] `esphome config espcure.yaml` passes with zero errors
- [ ] `http://espcure.local` loads and shows live sensor values
- [ ] Chamber temperature reads a plausible value
- [ ] Chamber humidity reads a plausible value
- [ ] Fan relay turns ON automatically at boot
- [ ] Status LED shows green (dim) when PID is idle
- [ ] OLED displays temperature and RH on Page 1 (if connected)
- [ ] Climate entity shows target 15.6 °C (60 °F)
- [ ] Dew-point humidity mode is active by default
- [ ] Both cure program switches OFF by default
- [ ] **Apply Dry Profile** sets 20 °C + 12.2 °C DP + dew-point mode ON
- [ ] HA device shows all entities after integration is added

---

## 8. Set up HA time sync

The midnight cure step-down cron requires accurate time. Ensure your Home Assistant timezone is correct:

**Settings → System → General → Time zone**

The ESP32 syncs time from HA on connect. Without this, the midnight cron will not fire at the right time.

---

## 9. Calibrate sensors

After the chamber has been running for 30 minutes, follow `docs/calibration.md` to apply temperature and humidity offsets. The SHT45 reads within ±0.1 °C from the factory but mounting position and airflow introduce small errors.

---

## 10. Subsequent OTA updates

After the first USB flash, all future updates are wireless:

```bash
esphome run espcure.yaml --device espcure.local
```

---

## Fallback / Recovery

If the ESP32 loses WiFi or cannot reach HA:
- It broadcasts a **`EspCure-Setup`** fallback WiFi AP (password: `ap_password` from secrets)
- Connect to this network and browse to `http://192.168.4.1`
- The controller continues operating with last-known setpoints during WiFi outage
- OTA and web UI remain available on the fallback AP
