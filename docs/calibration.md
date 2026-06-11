# Sensor Calibration

## SHT45 Temperature Calibration

The SHT45 has excellent accuracy (±0.1 °C typical) and very low self-heating (~0.1–0.2 °C at 3.3 V). Still run this procedure after install — mounting position and airflow affect the reading.

### Procedure

1. Let the fridge stabilize at room temperature with the door open for 30 minutes.
2. Place a calibrated reference thermometer next to the SHT45 inside the chamber.
3. Record both readings at steady state.
4. `offset = reference_reading - espcure_reading`

Example: Reference = 20.0 °C, ESPCure reading = 20.2 °C → offset = −0.2 °C

### Apply the offset

Edit `espcure.yaml`:

```yaml
sensor:
  - platform: sht4x
    temperature:
      id: chamber_temp
      name: "Chamber Temperature"
      filters:
        - offset: -0.2   # adjust to your measured value
```

Re-flash with `esphome run espcure.yaml`.

## SHT45 Humidity Calibration

The SHT45 factory RH accuracy is ±1.0 % (typical). For most installs no offset is needed, but verify with a saturated salt reference if you want tighter control:

1. Use a saturated salt solution to create a reference humidity environment:
   - Sodium chloride (table salt): ~75 % RH at room temperature
   - Magnesium chloride: ~33 % RH at room temperature
2. Place the SHT45 in a sealed container with the salt slurry for 2 hours.
3. Compare the ESPCure reading to the reference.
4. Apply offset the same way as temperature.

For most users, an offset of 0–1.5 % is sufficient.

## SHT45 On-Chip Heater

The SHT45 has a built-in heater to clear condensation from the sensor surface. It is disabled by default in `espcure.yaml` (`heater_max_duty: 0.0`). If you see the humidity reading suddenly peg to 100 % during rapid temperature drops, press the **Clear Sensor Condensation** button in HA — this logs a heater pulse warning; the firmware will resume normal readings after the next update cycle. Do not leave the heater enabled continuously — it will skew temperature and RH readings.

## DS18B20 (Cold Plate) Calibration

The DS18B20 accuracy is ±0.5 °C from the factory. For frost protection, ±0.5 °C is acceptable — no calibration needed unless you have a precision reference.

If calibrating: compare against an ice-water bath (0.0 °C reference) and apply an offset in the `filters` section.

## Dew Point Accuracy

Dew point is derived from temperature + RH via the Magnus formula. Combined accuracy after calibration is approximately ±0.3–0.5 °C dew point. This is sufficient for Cannatrol-style control (setpoint steps of 0.5–1.0 °C).

## Calibration Log

| Date | Sensor | Reference | ESPCure reading | Applied offset |
|---|---|---|---|---|
| — | SHT45 Temperature | — | — | 0.0 °C |
| — | SHT45 Humidity | — | — | 0.0 % |
| — | DS18B20 | — | — | 0.0 °C |
