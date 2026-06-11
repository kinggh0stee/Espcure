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

## 4. Verify connectivity

Open a browser to `http://espcure.local` (or the IP shown in logs). The ESPHome web interface should display all sensors and controls.

## 5. Add to Home Assistant

1. In HA: **Settings → Devices & Services → Add Integration → ESPHome**
2. Enter `espcure.local` (or IP address)
3. Enter the `api_encryption_key` from your `secrets.yaml`
4. All entities will appear under the **EspCure** device

## 6. First-run checklist

- [ ] Chamber temperature sensor reads a plausible value
- [ ] Cold plate temperature sensor reads (should be near ambient initially)
- [ ] Chamber humidity sensor reads a plausible value
- [ ] Fan relay turns on automatically on boot
- [ ] Climate entity shows in HA with target 12.8 °C
- [ ] Dehumidifier relay off by default
- [ ] Cure program switch off by default

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
