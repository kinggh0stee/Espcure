# Sensor Calibration

## SHT45 Temperature Calibration

The SHT45 has excellent accuracy (±0.1 °C typical) and very low self-heating (~0.1–0.2 °C at 3.3 V). Still run this procedure after install — mounting position and airflow affect the reading.

### Procedure

1. Let the chamber stabilize at room temperature with the door open for 30 minutes.
2. Place a calibrated reference thermometer next to the SHT45 inside the chamber.
3. Record both readings at steady state (wait for SHT45 to settle — 2–3 readings).
4. `offset = reference_reading − espcure_reading`

Example: Reference = 20.0 °C, ESPCure reading = 20.2 °C → offset = −0.2 °C

### Apply the offset

Edit `espcure.yaml` under the SHT45 sensor block:

```yaml
sensor:
  - platform: sht4x
    temperature:
      id: chamber_temp
      name: "Chamber Temperature"
      filters:
        - offset: -0.2   # adjust to your measured value
```

Re-flash with `esphome run espcure.yaml` or adjust at runtime and reflash once confirmed.

---

## SHT45 Humidity Calibration

The SHT45 factory RH accuracy is ±1.0 % (typical). For most installs no offset is needed. Verify with a saturated salt reference if you want tighter dew-point control:

| Salt | RH at 20 °C |
|---|---|
| Magnesium chloride (MgCl₂) | ~33 % |
| Sodium chloride (NaCl, table salt) | ~75 % |
| Potassium sulfate (K₂SO₄) | ~97 % |

### Procedure

1. Dissolve the salt in a small amount of water until a slurry forms (excess solid present).
2. Place the slurry and the SHT45 in a sealed container — do not let moisture contact the sensor directly.
3. Let equilibrate for 2 hours at a stable room temperature.
4. Compare ESPCure reading to the reference RH value.
5. Apply `offset` in the humidity `filters` block the same way as temperature.

For most users, a 0–1.5 % offset is sufficient.

---

## SHT45 On-Chip Heater

The SHT45 has a built-in heater to clear condensation from the sensor surface. It is **disabled by default** in `espcure.yaml` (`heater_max_duty: 0.0`).

If the humidity reading suddenly pegs to 100 % during rapid temperature drops, press the **Clear Sensor Condensation** button in HA or the device web UI. This logs a heater-pulse event; the firmware resumes normal readings after the next 30-second update cycle.

Do not leave the heater enabled continuously — it will bias both temperature and RH readings upward.

---

## Dew Point Accuracy

Dew point is derived from temperature + RH via the Magnus formula (no separate sensor). Combined uncertainty after calibration is approximately ±0.3–0.5 °C. This is sufficient for Cannatrol-style control (setpoint hysteresis defaults to ±0.5 °C).

To improve dew point accuracy, prioritize calibrating the temperature sensor first — a 0.2 °C temperature error introduces ~0.2 °C dew point error.

---

## Calibration Log

Fill in after first install:

| Date | Sensor | Reference | ESPCure reading | Applied offset |
|---|---|---|---|---|
| — | SHT45 Temperature | — | — | 0.0 °C |
| — | SHT45 Humidity | — | — | 0.0 % |
