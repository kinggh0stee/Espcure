# PID Tuning Log

The temperature control loop is a heat-only `climate.pid` component in ESPHome, driving the PTC heater relay (heat) via LEDC at 15 Hz. The Peltier is **not PID-driven**; it is controlled by a separate 30 s bang-bang loop that chases dew point or VPD setpoints.

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

The `PID Autotune` button in HA / web UI triggers ESPHome's built-in relay-feedback autotune. This characterises the **heater only** — the Peltier is bang-bang controlled by a separate dew-point/VPD loop and not part of the heat PID.

1. Let chamber stabilize below setpoint (e.g. 10 °C with door closed).
2. Set target temperature to 15.6 °C (60 °F) via the climate entity.
3. Press **PID Autotune** in the HA device page or device web UI.
4. Wait. The heater will oscillate deliberately. For a small fridge this typically takes 20–60 minutes.
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
| Very slow approach (> 1 h) | kp too low | Increase kp 25 % |
| Spiky noise on output | kd too high or sensor noise | Increase `derivative_averaging_samples` |
| Heater never activates | Chamber above setpoint or max safety ceiling engaged | Normal — heater only pulls up to 60 °F target; Peltier cools below |

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
