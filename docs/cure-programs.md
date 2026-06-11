# Cure Programs

## Control Mode Overview

EspCure supports two humidity control modes, selectable via the **Dew Point Control Mode** switch:

| Mode | Switch | Controls | Setpoint entity |
|---|---|---|---|
| **RH Mode** (default) | OFF | % Relative Humidity | `Humidity Setpoint` |
| **Dew Point Mode** | ON | Dew point °C | `Dew Point Setpoint` |

**Dew Point Mode is the Cannatrol-equivalent approach.** The Cannatrol displays dry-bulb temperature + dew point and controls the dehumidifier by maintaining a target dew point. When the cold plate drops below the air's dew point, moisture condenses on the plate and is removed — that's the dehumidification mechanism.

**RH Mode** is simpler and more familiar. Use it if you prefer working in % RH.

Both modes use the same dehumidifier relay and hysteresis logic — only the control variable changes.

---

## Built-in Programs

EspCure has two automated cure programs. Only one can run at a time — enabling one automatically disables the other.

### 18-Day Step-Down Program

Slow, conservative cure based on the rollitup.org cold-plate method.

| Setting | Value |
|---|---|
| Temperature | 55 °F (12.8 °C) |
| Control mode | RH % |
| Start humidity | 78 % |
| End humidity | 60 % |
| Step | −1 %/day at midnight |
| Duration | ~18 days |

**Enable**: Toggle **Cure Program (18-day)** switch ON — resets day counter to 0 and humidity setpoint to 78 %. Automatically switches to RH mode.

**Pause**: Toggle switch OFF. The current setpoint is retained.

**Resume**: Toggle ON again. Step-down continues from the current setpoint.

**Status sensor**: `Cure Program Status` shows e.g. `Day 3 — 75% RH target`.

---

### Cannatrol 4+4 Program

Fast, commercial-style cure using dew-point control. Matches the Cannatrol's default protocol.

| Phase | Days | Temp | Dew Point | RH Equivalent |
|---|---|---|---|---|
| Dry | 1–4 | 68 °F (20 °C) | 12.2 °C (54 °F) | ~61 % |
| Cure | 5–8 | 68 °F (20 °C) | 11.1 °C (52 °F) | ~57 % |

**Enable**: Toggle **Cannatrol 4+4 Program** switch ON. This automatically:
- Enables Dew Point Control Mode
- Sets temperature to 20.0 °C (68 °F)
- Sets dew point to 12.2 °C (dry phase)
- Resets the day counter

**Phase transition**: Midnight on day 5 drops the dew point setpoint to 11.1 °C automatically.

**Status sensor**: `Cannatrol Program Status` shows e.g. `Dry Phase — Day 2/4 (12.2°C DP)`.

---

## One-Tap Profile Presets

Three preset buttons are available on both the device web UI (`http://espcure.local`) and in Home Assistant:

| Button | Temp | Dew Point | Mode |
|---|---|---|---|
| **Apply Dry Profile** | 20 °C (68 °F) | 12.2 °C (54 °F) | Dew Point ON |
| **Apply Cure Profile** | 20 °C (68 °F) | 11.1 °C (52 °F) | Dew Point ON |
| **Apply Cold-Plate Profile** | 12.8 °C (55 °F) | — | Dew Point OFF (RH mode) |

These set all relevant setpoints instantly without modifying the cure program switch or day counter.

---

## Manual Humidity Control

When no program is running, set setpoints manually:

- **Humidity Setpoint** — target % RH (RH mode)
- **Humidity Hysteresis** — dead band ÷ 2; default 2 %, tighten to 1 % for precision
- **Dew Point Setpoint** — target dew point °C (dew point mode)
- **Dew Point Hysteresis** — dead band ÷ 2; default 0.5 °C

The **Humidity Error** and **Dew Point Error** diagnostic sensors show the current deviation from setpoint (positive = too humid).

---

## Which Protocol to Use?

| Protocol | Duration | Temp | Control mode | Best for |
|---|---|---|---|---|
| 18-day step-down | ~18 days | 55 °F (12.8 °C) | RH % | Slow, forgiving — cold plate actively condenses |
| Cannatrol 4+4 | ~8 days | 68 °F (20.0 °C) | Dew point | Faster — closer to commercial result |
| Cold-Plate Profile | Manual | 55 °F (12.8 °C) | RH % | Ongoing storage after cure |
| Cannatrol Storage | Manual | 68 °F (20.0 °C) | Dew point 12.2 °C | Long-term storage |

The rollitup method works better at lower temperatures where the Peltier is working harder and the cold plate actively condenses moisture. The Cannatrol method works at near-ambient temperature and relies on dew-point regulation to pace moisture loss.

---

## Home Assistant Automation Examples

### Alert: Cure Program Complete

```yaml
alias: "EspCure — Cure Program Complete"
triggers:
  - trigger: state
    entity_id: switch.espcure_cure_program_18_day
    from: "on"
    to: "off"
actions:
  - action: notify.mobile_app_your_phone
    data:
      title: "EspCure"
      message: "18-day cure program complete. Humidity is now at 60 %."
mode: single
```

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

### Alert: Temperature Out of Range

```yaml
alias: "EspCure — Temperature Alert"
triggers:
  - trigger: numeric_state
    entity_id: sensor.espcure_chamber_temperature
    above: 16
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
alias: "EspCure — Frost Protection"
triggers:
  - trigger: state
    entity_id: binary_sensor.espcure_frost_floor_active
    to: "on"
actions:
  - action: notify.mobile_app_your_phone
    data:
      title: "EspCure Warning"
      message: "Frost floor active — PID suspended until chamber warms."
mode: single
```

### Alert: Humidity Out of Range

```yaml
alias: "EspCure — Humidity Alert"
triggers:
  - trigger: numeric_state
    entity_id: sensor.espcure_chamber_humidity
    above: 80
    for:
      hours: 1
  - trigger: numeric_state
    entity_id: sensor.espcure_chamber_humidity
    below: 55
    for:
      hours: 1
actions:
  - action: notify.mobile_app_your_phone
    data:
      title: "EspCure Alert"
      message: >
        Chamber humidity out of range:
        {{ states('sensor.espcure_chamber_humidity') }} % RH
mode: single
```

### Auto-advance to Cure Phase (18-day program)

Manually transitions to a lower temperature and steady humidity setpoint after 7 days:

```yaml
alias: "EspCure — Switch to Cure Phase"
triggers:
  - trigger: numeric_state
    entity_id: number.espcure_cure_program_day
    above: 6
conditions:
  - condition: state
    entity_id: switch.espcure_cure_program_18_day
    state: "on"
actions:
  - action: climate.set_temperature
    target:
      entity_id: climate.espcure_chamber_temperature
    data:
      temperature: 12.8
  - action: number.set_value
    target:
      entity_id: number.espcure_humidity_setpoint
    data:
      value: 63
mode: single
```
