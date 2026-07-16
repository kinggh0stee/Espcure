# Peltier Cooling Loop

The Peltier (TEC) dehumidification loop is a **self-tuning proportional controller with adaptive bias**. It is separate from the temperature PID; it chases the dew-point setpoint autonomously, learning the chamber's steady-state offset over time so users rarely need to adjust it.

## Why Allende?

Previous versions used a simple on/off (bang-bang) loop: if dew point was above setpoint, turn on; below setpoint, turn off. Bang-bang works but wastes power running the TEC at full duty when partial duty would hold setpoint just as well. The Allende method replaces this with **continuous duty 0–100%** and **adaptive bias learning** — the controller self-tunes its steady-state operating point, so you set it and mostly forget it.

## How It Works

The loop runs every 20 seconds (vs. the old 30 s bang-bang) with the following priority chain:

1. **Frost guard** (hard override) — if chamber temp < frost floor, force Peltier OFF.
2. **High-temp safety ceiling** — if chamber temp > ceiling, force Peltier ON at 100%.
3. **Humidity mode gate** — if dew-point mode is OFF, force Peltier OFF.
4. **Sensor fault guard** — if dew point is invalid (NaN), force Peltier OFF.
5. **Dry floor** — if chamber RH < dry floor, force Peltier OFF until RH recovers. Bias integrator frozen.
6. **Allende math** — proportional + adaptive bias control.

The Allende formula itself (step 6):

```
output = (0.5 + error × gain) × bias
```

- **Error** = dew point (measured) − dew point (setpoint). Positive = air is too humid.
- **Gain** (`Cool Gain (Allende)`, default 0.03125) = proportional scaler in duty/%°C. Controls response speed.
- **Bias** (`Cool Bias (Allende)`) = adaptive integrator (0.0–3.0, default start 1.0). Self-learns the chamber's offset.

**Adaptive bias** ticks every 20 s (unless dry floor or frost guard is active):
- If `|error| > deadband`, the bias drifts ±0.01 towards correction (learns).
- If `|error| < deadband`, bias freezes (satisfied).
- Clamped 0.0–3.0 so it can't drift to infinity.

**Satisfied cutoff** (safety feature): once dew point is more than one deadband **below** the setpoint (already dry enough), the Peltier is forced to 0% duty — this prevents over-cooling.

**Dry floor** (step 5): If chamber RH drops below `Min Chamber RH (Dry Floor)` (default 55%), the Peltier is suspended and the bias integrator is frozen (no adaptation). Peltier resumes once RH recovers 3% above the floor (e.g. 58% if floor is 55%). This prevents over-drying if condensation runs away. The dew-point setpoint schedule continues advancing — only the Peltier duty is gated.

## Tuning

Four entities control the loop:

| Entity | Default | Adjustable? | When to tune |
|---|---|---|---|
| **Cool Gain (Allende)** | 0.03125 | Yes, 0.0–0.2 | Sluggish response → increase; oscillating wildly → decrease |
| **Dew Point Deadband** | 0.1 °C | Yes, 0.1–2.0 °C | Narrow = frequent small adjustments (more wear); wide = slower but gentle |
| **Cool Bias (Allende)** | diagnostic | No, read-only | Shows live integrator value; should settle ~1.0 at equilibrium |
| **Reset Cool Bias** | button | Yes | Press after a long frost event or if bias drifts to extreme (0 or 3) |

### Interpreting Cool Bias

- **Settling around 1.0** = normal. The loop has learned the chamber's steady-state offset.
- **Pinned at 0.0** = bias has saturated downward. Either the **gain is too small** (increase it 0.005–0.01) or the **deadband is too wide** (narrow it 0.1–0.05 °C). The loop is struggling to cool enough.
- **Pinned at 3.0** = bias has saturated upward. Either the **gain is too large** (decrease it 0.005–0.01) or the **deadband is too narrow** (widen it 0.1–0.2 °C). The loop is over-cooling.

### Gain Adjustment (Start Conservative)

The default gain 0.03125 (1/32) is conservative: each °C of error produces ~3% duty. This suits Peltiers with thermal inertia (they overshoot easily). If the chamber is very slow to respond:

1. Increase gain by 0.005–0.01 increments (e.g. 0.03125 → 0.04).
2. Let it settle 1–2 hours and observe the bias trend.
3. If bias is creeping toward 0, stop; if stable ~1.0, you can increase more.

If the Peltier oscillates (undershoots then overshoots), reduce gain 0.005–0.01.

### Deadband Tuning (Advanced)

Default 0.1 °C is tight — the loop adapts on every tick if error exceeds ±0.1. This is stable for most chambers.

- **Narrow (0.05 °C)** = even more frequent adaptation. Only if response is very sluggish despite higher gain.
- **Widen (0.2–0.3 °C)** = less frequent adaptation. Use if bias oscillates around 1.0 (the loop is over-correcting).

### Manual Bias Reset

Press **Reset Cool Bias** to set `cool_bias` back to 1.0 if:
- Power was lost and the chamber was ice-cold (frost guard forced Peltier off for hours). The bias learned to "always full power" and needs a restart.
- You changed the gain significantly and the old bias is stale.
- The bias drifted to 0 or 3 (saturated) and won't recover because the deadband is too wide.

After reset, the loop re-learns over the next 1–2 hours of operation.

## Satisfied Cutoff

Once the dew point is **more than one deadband below the setpoint** (e.g. setpoint 12.2 °C, deadband 0.1 °C, dew point now 12.05 °C or lower), the Peltier is forced to 0% to prevent unnecessary over-cooling. This is a deliberate safety feature: without it, the proportional formula's 0.5 baseline would keep the TEC running at partial duty near setpoint, relying on the bias integrator to slowly decay toward zero (tens of minutes) before cooling actually stopped. The cutoff forces an immediate stop instead — the chamber is already sufficiently dry.

This interacts with gain and bias:

- If gain is very high and bias is large, the Peltier can overshoot below setpoint, triggering satisfied-cutoff and stopping abruptly. The bias then creeps back up over the next few ticks. Reduce gain or narrow deadband to avoid this "bouncing."

## Allende vs. PID

The temperature control loop is a **heat-only PID** (tuned Kp/Ki/Kd); the Peltier uses **Allende** (proportional + learning). They are decoupled by design:

- **PID** (temperature): constant coefficients, deterministic response. Reflects care & tuning effort.
- **Allende** (humidity): adapts its own bias autonomously. Reflects simplicity & "set and forget" philosophy.

The Peltier cold plate is the sole dehumidification mechanism — the heater only holds the temperature floor and plays no role in moisture removal. The two loops run independently and don't interfere with each other.
