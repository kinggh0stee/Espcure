# PID Tuning Log

The temperature control loop is a `climate.pid` component in ESPHome, driving the Peltier SSR (cool) and PTC heater relay (heat) through `slow_pwm` outputs with a 20 s period.

## Current Parameters

```yaml
control_parameters:
  kp: 0.35
  ki: 0.005
  kd: 1.2
  max_integral: 1.0
  output_averaging_samples: 5
  derivative_averaging_samples: 5
deadband_parameters:
  threshold_high: 0.5
  threshold_low: -0.5
  kp_multiplier: 0.1
  ki_multiplier: 0.05
  kd_multiplier: 0.0
```

These are initial defaults. Run the autotune procedure after install to get values specific to your fridge.

## Live PID Tuning (no reflash needed)

EspCure exposes `PID Kp`, `PID Ki`, and `PID Kd` as number entities — available on both the device web UI (`http://espcure.local`) and in Home Assistant. Changing any value instantly applies it to the running PID controller via `climate.pid.set_control_parameters`.

Values are persisted across reboots (`restore_value: true`) and automatically re-applied at boot. You no longer need to edit the YAML or reflash to tune the PID.

**After tuning**: Update the `control_parameters` block in `espcure.yaml` to match your tuned values so the YAML stays the source of truth, and log them below.

## Autotune Procedure

The `PID Autotune` button in HA / web UI triggers ESPHome's built-in relay-feedback autotune.

1. Let chamber stabilize at a temperature above setpoint (e.g. room temp) with the door closed.
2. Set target temperature to 12.8 °C (55 °F) via the climate entity.
3. Press **PID Autotune** in the HA device page or device web UI.
4. Wait. The fridge will oscillate deliberately. For a small thermoelectric fridge this takes 30–90 minutes.
5. Watch ESPHome logs (`esphome logs espcure.yaml`) for:
   ```
   [I][pid.autotune:xxx]: PID Autotune finished!
   [I][pid.autotune:xxx]:   Calculated kp=X, ki=Y, kd=Z
   ```
6. Apply the new values via the `PID Kp/Ki/Kd` sliders in the web UI or HA — no reflash needed.
7. Update `control_parameters` in `espcure.yaml` and log them below.

## Diagnostic Quick Reference

| Symptom | Likely cause | Fix |
|---|---|---|
| Oscillates around setpoint ±2 °C | kp too high | Reduce kp 20–30 % |
| Overshoots then slowly recovers | ki too high (integral windup) | Reduce ki, verify `max_integral: 1.0` |
| Never reaches setpoint (offset) | ki too low | Increase ki 50 % |
| Very slow approach (> 2 h) | kp too low | Increase kp 25 % |
| Spiky noise on output | kd too high or sensor noise | Increase `derivative_averaging_samples` |
| PID never uses heat output | Fridge ambient too warm, or heater undersized | Verify heater wattage; accept if cooling-only is sufficient |

---

## Tuning Log

### Initial defaults — 2026-06-11

**Source**: Estimated from typical small thermoelectric fridge (30–50 L).
**Conditions**: Not yet installed; baseline values pending autotune.

```yaml
kp: 0.35
ki: 0.005
kd: 1.2
```

*Replace this entry with autotune results after first install.*
