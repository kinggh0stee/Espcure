# Sensor Calibration

## SHT31 Temperature Calibration

The SHT31 has slight self-heating (~1–2 °C at 3.3 V continuous power). The actual offset depends on mounting position, airflow, and ambient temperature.

### Procedure

1. Let the fridge stabilize at room temperature with the door open for 30 minutes.
2. Place a calibrated reference thermometer next to the SHT31 inside the chamber.
3. Record both readings at steady state.
4. `offset = reference_reading - espcure_reading`

Example: Reference = 20.0 °C, ESPCure reading = 21.8 °C → offset = −1.8 °C

### Apply the offset

Edit `espcure.yaml`:

```yaml
sensor:
  - platform: sht3xd
    temperature:
      id: chamber_temp
      name: "Chamber Temperature"
      filters:
        - offset: -1.8   # adjust to your measured value
```

Re-flash with `esphome run espcure.yaml`.

## SHT31 Humidity Calibration

1. Use a saturated salt solution to create a reference humidity environment.
   - Sodium chloride (table salt): ~75 % RH at room temperature
   - Magnesium chloride: ~33 % RH at room temperature
2. Place the SHT31 in a sealed container with the salt slurry for 2 hours.
3. Compare the ESPCure reading to the reference.
4. Apply offset in the same way as temperature.

For most users, a humidity offset of 0–3 % is typical.

## DS18B20 (Cold Plate) Calibration

The DS18B20 accuracy is ±0.5 °C from the factory. For frost protection, ±0.5 °C is acceptable — no calibration needed unless you have a precision reference.

If calibrating: compare against an ice-water bath (0.0 °C reference) and apply an offset in the `filters` section.

## Calibration Log

| Date | Sensor | Reference | ESPCure reading | Applied offset |
|---|---|---|---|---|
| — | SHT31 Temperature | — | — | 0.0 °C |
| — | SHT31 Humidity | — | — | 0.0 % |
| — | DS18B20 | — | — | 0.0 °C |
