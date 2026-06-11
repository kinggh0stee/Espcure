# Setup Guide

## Prerequisites

- ESPHome installed: `pip install esphome`
- Home Assistant running (for HA API integration and time sync)
- Hardware assembled per `docs/hardware.md`
- USB-to-serial adapter or direct USB connection to ESP32

## 1. Prepare secrets

```bash
cp secrets.yaml.example secrets.yaml
```

Edit `secrets.yaml`:

```yaml
wifi_ssid: "YourNetwork"
wifi_password: "YourPassword"
ap_password: "espcure-setup"
api_encryption_key: "<generate below>"
ota_password: "<choose a strong password>"
```

Generate an API key:
```bash
python3 -c "import base64,os; print(base64.b64encode(os.urandom(32)).decode())"
```

## 2. Validate config

```bash
esphome config espcure.yaml
```

Fix any reported errors before proceeding.

## 3. First flash (USB)

Connect the ESP32 via USB. Hold the BOOT button if the device does not enter flash mode automatically.

```bash
esphome run espcure.yaml
```

When complete, the ESP32 will reboot and connect to your WiFi. The onboard LED will blink during connection.

## 4. Open the device web UI

Browse to **`http://espcure.local`** (or the IP address shown in logs).

The device-hosted dashboard gives full control without Home Assistant:

| Section | What you get |
|---|---|
| **Sensors** | Chamber temp (°C + °F), RH, dew point, VPD, error values |
| **Climate** | Temperature PID card — adjust setpoint, see cooling/heating state |
| **Controls** | Cure programs, dehumidifier, fan, dew-point mode toggle |
| **Presets** | Apply Dry / Cure / Cold-Plate profile in one tap |
| **PID Tuning** | Adjust Kp/Ki/Kd live — changes apply without reflash |
| **Status** | Chamber Status, Humidity Control Mode, program progress |
| **Dark mode** | Toggle in the top-right corner of the UI (follows system preference by default) |

The web UI runs entirely from the ESP32's flash — no internet access required.

## 5. Add to Home Assistant

1. In HA: **Settings → Devices & Services → Add Integration → ESPHome**
2. Enter `espcure.local` (or IP address)
3. Enter the `api_encryption_key` from your `secrets.yaml`
4. All entities will appear under the **EspCure** device

### Import the dashboard

A ready-to-use Lovelace dashboard is at `docs/ha-dashboard.yaml`. To import:

1. In HA: **Settings → Dashboards → Add Dashboard**
2. Switch to YAML mode and paste the contents of `docs/ha-dashboard.yaml`

## 6. First-run checklist

- [ ] `http://espcure.local` loads the web dashboard
- [ ] Chamber temperature sensor reads a plausible value
- [ ] Chamber humidity sensor reads a plausible value
- [ ] Fan relay turns on automatically on boot
- [ ] Climate entity shows with target 12.8 °C (55 °F)
- [ ] Dehumidifier relay off by default
- [ ] Both cure program switches off by default
- [ ] Apply Dry Profile button sets 20 °C + 12.2 °C DP + dew-point mode ON

## 7. Set up HA time sync

The daily cure step-down uses `time.homeassistant`. Ensure your Home Assistant has the correct timezone set:

**Settings → System → General → Time zone**

The ESP32 syncs time from HA on connect; the midnight cron will not fire correctly without this.

## 8. Subsequent OTA updates

After first flash, all future updates are wireless:

```bash
esphome run espcure.yaml --device espcure.local
```

## Fallback / Recovery

If the ESP32 loses WiFi or cannot reach HA:
- It broadcasts `EspCure-Setup` WiFi AP (password: `ap_password` from secrets)
- Connect to this AP and open `http://192.168.4.1` to reconfigure
- The controller continues operating with last-known setpoints during WiFi outage
