# Cure Programs

## Control Architecture Overview

EspCure uses a **decoupled control topology**:

- **Temperature (heater only)**: PID loop targets 17.2 °C by default, rarely activates (chamber floats 17–19 °C). A safety ceiling at 27 °C forces the Peltier ON above that point regardless of humidity demand.
- **Humidity (Peltier cold plate)**: Self-tuning Allende loop on dew point, runs every 20 s with continuous duty (0–100%, learned via adaptive bias), condensing moisture from the air onto the Peltier cold plate. This is the sole dehumidification mechanism. See `docs/cooling-loop.md` for tuning details.
- **Fan (GPIO5)**: runs **continuously while a cure program is active** (constant air circulation for even drying); otherwise ON when the Peltier is cooling OR the heater is heating, and OFF when idle with no program.

## Humidity Control Mode

The Peltier is driven by **Dew Point** control — the only user-selectable humidity mode:

| Mode | Controls | Setpoint entity | How it works |
|---|---|---|---|
| **Dew Point Mode** (default, always on) | Dew point °C | `Dew Point Setpoint` | Peltier chases dew point; cold plate condenses when below air DP |

> A VPD control mode still exists in the firmware (`use_vpd_control`, `vpd_setpoint`, `vpd_hysteresis`, plus the VPD sensors) but is `internal: true` — hidden from the web UI and Home Assistant, so it can't be selected. Dew Point is the single humidity mode. To re-enable VPD, remove the `internal: true` flags in `espcure.yaml` (see the note in `CLAUDE.md`).

---

## Built-in Program

One automated cure program is available. Time sync is preferred but not required — the program self-heals missed ticks and operates with SNTP fallback.

### 10-Day Dry Program

Proven dew-point recipe with a controlled ramp and steady-state holds. This replaces the previous 18-day RH-based program.

Temperature stays at 17.2 °C throughout — the heater holds the floor while the Peltier chases dew point.

| Day (shown) | Dew Point | Temp | Notes |
|---|---|---|---|
| 1 | 15.6 °C | 17.2 °C | Ramp start — set the moment the program is enabled |
| 2 | 13.9 °C | 17.2 °C | Ramp midpoint |
| 3–6 | 12.2 °C | 17.2 °C | Dry hold (4 days) |
| 7–10 | 11.1 °C | 17.2 °C | Cure hold (4 days); program auto-disables after 10 days elapse |

**Enable**: Toggle the **10-Day Dry Program** switch ON. This automatically:
- Enables Dew Point Control Mode
- Sets the temperature target to 17.2 °C
- Sets the dew point to 15.6 °C (ramp start)
- Resets the day counter (shows Day 1)
- Anchors the program start time to the current moment

**The 2-day ramp**: dew point starts at 15.6 °C on enable, reaches 13.9 °C one day later, and reaches 12.2 °C two days from start — a gentle ramp that lets the Peltier begin condensing without aggressively drying the material.

**Day progression** (every 24 hours from program start, self-healing):
- Day 0: dew point 15.6 °C (ramp origin, set on enable)
- Day 1: dew point 13.9 °C (ramp midpoint)
- Days 2–5: hold 12.2 °C (dry phase, 4 days)
- Days 6–9: hold 11.1 °C (cure phase, 4 days)
- Day ≥10: program auto-disables

Days are true 24-hour periods from program start, not calendar-midnight boundaries. A program started at 11 PM on one day is not treated as "two days old" the next morning — it ages by actual hours elapsed. If the device loses connection or restarts mid-program, the day counter catches up on the next valid time source (HA time preferred, SNTP fallback, or manual edit).

**Manual day edit**: Dragging the **10-Day Program Day** number re-anchors the program. Setting it to day N is equivalent to re-starting the program N days ago, re-locking the schedule.

**Status sensor**: `10-Day Program Status` shows e.g. `Day 3/10 — Dry 12.2°C`.

---

## Manual Humidity Control

When no program is running, set the dew-point target manually:

**Dew Point Mode** (the only selectable mode):
- **Dew Point Setpoint** — target dew point °C
- **Dew Point Deadband** — ± band around setpoint (full value, not halved); default 0.1 °C. Gates the Allende bias adaptation and the satisfied-cutoff — see `docs/cooling-loop.md`

The **Dew Point Error** diagnostic sensor shows the current deviation from dew-point setpoint (positive = too humid).

---


## Safety Controls

### Frost Floor (Min Chamber Temp)

If chamber air temperature (SHT45) drops below the floor (default 4 °C), the Peltier is suspended until the chamber recovers 2 °C above that point. The heater continues running to aid recovery. Adjust in HA via the **Min Chamber Temperature** number entity.

### Dry Floor (Min Chamber RH)

If chamber relative humidity drops below the floor (default 55%), the Peltier is suspended until humidity recovers 3% above that point. The dry floor mirrors the frost floor on the humidity side — a safety net against over-drying the product. Chamber RH typically stays 65–75% during normal operation, so the 55% floor is rarely triggered except in a runaway dehumidification scenario. Adjust in HA via the **Min Chamber RH (Dry Floor)** number entity (range 30–60%).

Note: the dew-point setpoint schedule continues advancing while the dry floor holds the Peltier off — only the duty output is gated.

### Safety Ceiling (Max Chamber Temp)

If chamber air temperature exceeds the ceiling (default 27 °C), the Peltier is forced ON regardless of humidity demand, giving temperature an emergency downward authority. User-adjustable 22–32 °C in HA via **Max Chamber Temperature** number entity. This does not normally activate during standard 17–19 °C operation.

---

## Home Assistant Automation Examples

### Alert: 10-Day Dry Program Complete

```yaml
alias: "EspCure — 10-Day Dry Complete"
triggers:
  - trigger: state
    entity_id: switch.espcure_10_day_dry_program
    from: "on"
    to: "off"
actions:
  - action: notify.mobile_app_your_phone
    data:
      title: "EspCure"
      message: "10-Day Dry program complete. Chamber is in hold mode at 11.1 °C DP."
mode: single
```

### Alert: Temperature Out of Range

```yaml
alias: "EspCure — Temperature Alert"
triggers:
  - trigger: numeric_state
    entity_id: sensor.espcure_chamber_temperature
    above: 22
    for:
      minutes: 30
  - trigger: numeric_state
    entity_id: sensor.espcure_chamber_temperature
    below: 10
    for:
      minutes: 30
actions:
  - action: notify.mobile_app_your_phone
    data:
      title: "EspCure Alert"
      message: >
        Chamber temperature out of range:
        {{ states('sensor.espcure_chamber_temperature') }} °C
mode: single
```

### Alert: Frost Protection Triggered

```yaml
alias: "EspCure — Frost Protection Active"
triggers:
  - trigger: state
    entity_id: binary_sensor.espcure_frost_floor_active
    to: "on"
actions:
  - action: notify.mobile_app_your_phone
    data:
      title: "EspCure Warning"
      message: "Frost floor active — Peltier suspended until chamber warms."
mode: single
```

### Alert: Dew Point Out of Range

```yaml
alias: "EspCure — Dew Point Alert"
triggers:
  - trigger: numeric_state
    entity_id: sensor.espcure_chamber_dew_point
    above: 15
    for:
      hours: 1
  - trigger: numeric_state
    entity_id: sensor.espcure_chamber_dew_point
    below: 8
    for:
      hours: 1
actions:
  - action: notify.mobile_app_your_phone
    data:
      title: "EspCure Alert"
      message: >
        Chamber dew point out of range:
        {{ states('sensor.espcure_chamber_dew_point') }} °C
mode: single
```
