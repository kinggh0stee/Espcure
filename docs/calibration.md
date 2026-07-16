# Sensor Calibration

## SHT45 Temperature Calibration

The SHT45 has excellent accuracy (±0.1 °C typical) and very low self-heating (~0.1–0.2 °C at 3.3 V). Still run this procedure after install — mounting position and airflow affect the reading.

> **Using an SHT31?** The SHT31-D is supported via the `sht_platform: sht3xd` substitution. It is less accurate (±0.3 °C / ±2 % RH) and self-heats more (~0.3 °C). **Re-run this calibration whenever you swap between the SHT31 and SHT45** — the offset is sensor-specific and the two chips will not share the same correction.

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

## On-Chip Heater (Clear Sensor Condensation)

Both the SHT31 and SHT45 have a built-in resistive heater for evaporating condensation off the sensing element. It is **off during normal operation** so it never biases readings.

If the humidity reading pegs near 100 % after a rapid temperature drop (condensation on the sensor face), press the **Clear Sensor Condensation** button in HA or the device web UI.

The button works on whichever sensor is selected, via the `sht_heater_on`/`sht_heater_off` substitutions. On the **SHT31** (`sht3xd`) it pulses the real on-chip heater (`set_heater_enabled(true/false)`) for one measurement cycle, then takes a clean reading. The **SHT45** (`sht4x`) has **no on-demand heater API** — its heater is config-time only — so on the SHT45 the substitutions are no-ops (`";"`) and the button simply forces a fresh reading. (The firmware ships with the SHT45 active.)

Avoid pressing the button repeatedly — the heater temporarily biases both temperature and RH upward, and the effect clears within one update cycle after it's disabled.

---

## Dew Point Accuracy

Dew point is derived from temperature + RH via the Magnus formula (no separate sensor). Combined uncertainty after calibration is approximately ±0.3–0.5 °C. This is sufficient for Cannatrol-style control (Dew Point Deadband defaults to ±0.1 °C).

To improve dew point accuracy, prioritize calibrating the temperature sensor first — a 0.2 °C temperature error introduces ~0.2 °C dew point error.

---

## Calibration Log

Fill in after first install:

| Date | Sensor | Reference | ESPCure reading | Applied offset |
|---|---|---|---|---|
| — | SHT45 Temperature | — | — | 0.0 °C |
| — | SHT45 Humidity | — | — | 0.0 % |
