# Cure Programs

## Control Architecture Overview

EspCure uses a **decoupled control topology**:

- **Temperature (heater only)**: PID loop targets 15.6 °C by default, rarely activates (chamber floats 17–19 °C). A safety ceiling at 27 °C forces the Peltier ON above that point regardless of humidity demand.
- **Humidity (Peltier cold plate)**: Bang-bang loop on dew point, runs every 30 s at full 15 Hz, condensing moisture from the air onto the Peltier cold plate. This is the sole dehumidification mechanism.
- **Fan (GPIO5)**: runs **continuously while a cure program is active** (constant air circulation for even drying); otherwise ON when the Peltier is cooling OR the heater is heating, and OFF when idle with no program.

## Humidity Control Mode

The Peltier is driven by **Dew Point** control — the only user-selectable humidity mode:

| Mode | Controls | Setpoint entity | How it works |
|---|---|---|---|
| **Dew Point Mode** (default, always on) | Dew point °C | `Dew Point Setpoint` | Peltier chases dew point; cold plate condenses when below air DP |

> A VPD control mode still exists in the firmware (`use_vpd_control`, `vpd_setpoint`, `vpd_hysteresis`, plus the VPD sensors) but is `internal: true` — hidden from the web UI and Home Assistant, so it can't be selected. Dew Point is the single humidity mode. To re-enable VPD, remove the `internal: true` flags in `espcure.yaml` (see the note in `CLAUDE.md`).

---

## Built-in Programs

Two automated cure programs are available. Enabling one automatically disables the other. Both require Home Assistant time sync (midnight cron).

### Cannatrol 4+4 Program

Fast, commercial-style cure using dew-point control. Matches the Cannatrol's default protocol.

| Phase | Days | Temp | Dew Point |
|---|---|---|---|
| Dry | 1–4 | 20 °C | 12.2 °C |
| Cure | 5–8 | 20 °C | 11.1 °C |

**Enable**: Toggle **Cannatrol 4+4 Program** switch ON. This automatically:
- Enables Dew Point Control Mode
- Sets temperature target to 20.0 °C
- Sets dew point to 12.2 °C (dry phase)
- Resets the day counter

**Phase transition**: Midnight on day 5 drops the dew point setpoint to 11.1 °C.

**Status sensor**: `Cannatrol Program Status` shows e.g. `Dry Phase — Day 2/4 (12.2°C DP)`.

---

### 10-Day Dry Program

Proven dew-point recipe with a controlled ramp and steady-state holds. This replaces the previous 18-day RH-based program.

Temperature stays at 15.6 °C throughout — the heater holds the floor while the Peltier chases dew point.

| Day (shown) | Dew Point | Temp | Notes |
|---|---|---|---|
| 1 | 15.6 °C | 15.6 °C | Ramp start — set the moment the program is enabled |
| 2 | 13.9 °C | 15.6 °C | Ramp midpoint |
| 3–6 | 12.2 °C | 15.6 °C | Dry hold (4 days) |
| 7–10 | 11.1 °C | 15.6 °C | Cure hold (4 days); program auto-disables at midnight after day 10 |

**Enable**: Toggle the **10-Day Dry Program** switch ON. This automatically:
- Enables Dew Point Control Mode (disables Cannatrol 4+4)
- Sets the temperature target to 15.6 °C
- Sets the dew point to 15.6 °C (ramp start)
- Resets the day counter (shows Day 1)

**The 2-day ramp**: dew point starts at 15.6 °C on enable, drops to 13.9 °C at the first midnight, and reaches 12.2 °C at the second — a gentle ramp that lets the Peltier begin condensing without aggressively drying the material.

**Day progression** (at each midnight):
- Day 1 → 2: dew point 15.6 → 13.9 °C
- Day 2 → 3: dew point 13.9 → 12.2 °C (ramp complete)
- Days 3–6: hold 12.2 °C (dry phase, 4 days)
- Day 6 → 7: dew point 12.2 → 11.1 °C (cure phase begins)
- Days 7–10: hold 11.1 °C (cure phase, 4 days)
- After day 10's midnight: program auto-disables

**Status sensor**: `10-Day Program Status` shows e.g. `Day 3/10 — Dry 12.2°C`.

---

## Manual Humidity Control

When no program is running, set the dew-point target manually:

**Dew Point Mode** (the only selectable mode):
- **Dew Point Setpoint** — target dew point °C
- **Dew Point Hysteresis** — dead band ÷ 2; default 0.5 °C

The **Dew Point Error** diagnostic sensor shows the current deviation from dew-point setpoint (positive = too humid).

---

## Program Comparison

| Program | Duration | Temp | Dew Point | Best for |
|---|---|---|---|---|
| **Cannatrol 4+4** | ~8 days | 20 °C | 12.2→11.1 °C | Fast cure; commercial-style; near-ambient |
| **10-Day Dry** | 10 days | 15.6 °C | 15.6→13.9→12.2→11.1 °C | Proven recipe; gentle ramp; slower drying |
| **Manual Dew Point** | Ongoing | User-set | User-set | Storage or custom protocol |

**Why two programs?** Cannatrol 4+4 starts hard (12.2 °C DP day 1) and is faster. The 10-Day Dry ramps gently from 15.6 °C DP to avoid shocking the material.

---

## Safety Controls

### Frost Floor (Min Chamber Temp)

If chamber air temperature (SHT45) drops below the floor (default 4 °C), the Peltier is suspended until the chamber recovers 2 °C above that point. The heater continues running to aid recovery. Adjust in HA via the **Min Chamber Temperature** number entity.

### Safety Ceiling (Max Chamber Temp)

If chamber air temperature exceeds the ceiling (default 27 °C), the Peltier is forced ON regardless of humidity demand, giving temperature an emergency downward authority. User-adjustable 22–32 °C in HA via **Max Chamber Temperature** number entity. This does not normally activate during standard 17–19 °C operation.

---

## Home Assistant Automation Examples

### Alert: Cannatrol Program Complete

```yaml
alias: "EspCure — Cannatrol Program Complete"
triggers:
  - trigger: state
    entity_id: switch.espcure_cannatrol_4_4_program
    from: "on"
    to: "off"
actions:
  - action: notify.mobile_app_your_phone
    data:
      title: "EspCure"
      message: "Cannatrol 4+4 program complete. Chamber is in hold mode."
mode: single
```

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
