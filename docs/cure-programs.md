# Cure Programs

## Control Mode Overview

EspCure supports two humidity control modes, selectable via the **Dew Point Control Mode** switch in HA:

| Mode | Switch | Controls | Setpoint entity |
|---|---|---|---|
| **RH Mode** (default) | OFF | % Relative Humidity | `Humidity Setpoint` |
| **Dew Point Mode** | ON | Dew point °C | `Dew Point Setpoint` |

**Dew Point Mode is the Cannatrol-equivalent approach.** The Cannatrol displays dry-bulb temperature + dew point and controls the dehumidifier by maintaining a target dew point. When the cold plate drops below the air's dew point, moisture condenses on the plate and is removed — that's the dehumidification mechanism.

**RH Mode** is simpler and more familiar. Use it if you prefer working in % RH.

Both modes use the same dehumidifier relay and hysteresis logic — only the control variable changes.

---

## What the Cure Program Does

The built-in cure program automates the humidity step-down protocol for curing:

1. **Day 0**: Set humidity setpoint to 78 % RH — this is the starting point that prevents the dehumidifier from cycling too aggressively and freezing the cold plate.
2. **Each midnight**: Humidity setpoint decreases by 1 %.
3. **Day 18**: Setpoint reaches 60 % RH — program turns itself off.

This mirrors the manual protocol from the rollitup.org reference: start high, step down slowly, giving material time to equalize moisture.

## Enabling the Cure Program

In Home Assistant, toggle **Cure Program** on. The switch resets the day counter to 0 and the humidity setpoint to 78 %.

To pause: toggle the switch off. The current setpoint is retained.
To resume: toggle back on — it will continue the step-down from the current setpoint.

## Manual Humidity Control

When the cure program is off, set humidity manually via the **Humidity Setpoint** number entity. Adjust **Humidity Hysteresis** to control how tightly the dehumidifier cycles (2 % is a good starting point — tighten to 1 % for more precision, loosen to 3 % to reduce cycling).

## Home Assistant Automation Examples

### Alert: Cure Program Complete

```yaml
alias: "EspCure — Cure Program Complete"
description: "Notify when the automated cure program finishes"
triggers:
  - trigger: state
    entity_id: switch.espcure_cure_program
    from: "on"
    to: "off"
actions:
  - action: notify.mobile_app_your_phone
    data:
      title: "EspCure"
      message: "Cure program complete. Humidity is now at 60 %."
mode: single
```

### Alert: Temperature Out of Range

```yaml
alias: "EspCure — Temperature Alert"
description: "Notify if chamber temperature drifts out of acceptable range"
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
description: "Immediate alert when frost guard disables the Peltier"
triggers:
  - trigger: state
    entity_id: binary_sensor.espcure_frost_protection_active
    to: "on"
actions:
  - action: notify.mobile_app_your_phone
    data:
      title: "EspCure Warning"
      message: "Frost protection activated. Peltier disabled until cold plate warms above 4 °C."
mode: single
```

### Alert: Humidity Out of Range

```yaml
alias: "EspCure — Humidity Alert"
description: "Notify if humidity drifts dangerously high or low"
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

## Dry-and-Cure Two-Phase Protocol

Based on the rollitup.org reference build:

**Phase 1 — Dry (Days 0–7)**
- Temperature: 60 °F (15.5 °C) — slightly warmer than cure phase
- Humidity: Start 78 %, step down 1 %/day to 71 %
- Fans: ON continuous

**Phase 2 — Cure (Days 7–25)**
- Temperature: 55 °F (12.8 °C) — default EspCure setpoint
- Humidity: 62–65 % RH steady
- Fans: ON continuous

You can implement this two-phase transition manually in HA:

```yaml
alias: "EspCure — Switch to Cure Phase"
description: "Transition from dry to cure phase on day 7"
triggers:
  - trigger: numeric_state
    entity_id: number.espcure_cure_program_day
    above: 6
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

---

## Cannatrol 4+4 Protocol (Dew Point Mode)

The Cannatrol's default protocol is faster and uses dew point control instead of raw RH.

**Prerequisites**: Enable **Dew Point Control Mode** switch in HA before starting.

**Phase 1 — Dry (Days 0–4)**
- Temperature: 68 °F (20.0 °C)
- Dew point setpoint: 12.2 °C (54 °F dew point) → 61 % RH equivalent
- Fans: ON continuous

**Phase 2 — Cure (Days 4–8)**
- Temperature: 68 °F (20.0 °C)
- Dew point setpoint: 11.1 °C (52 °F dew point) → ~57 % RH equivalent
- Fans: ON continuous

**Storage**
- Same as Dry phase: 68 °F / 12.2 °C dew point

### HA Automation: Cannatrol 4+4 Start

```yaml
alias: "EspCure — Start Cannatrol 4+4 Protocol"
description: "Set up Dew Point mode at Cannatrol dry-phase defaults"
triggers:
  - trigger: state
    entity_id: input_button.espcure_start_cannatrol  # create a helper button in HA
    to: ~
actions:
  # Enable dew point control mode
  - action: switch.turn_on
    target:
      entity_id: switch.espcure_dew_point_control_mode
  # Set temperature to 68°F (20°C)
  - action: climate.set_temperature
    target:
      entity_id: climate.espcure_chamber_temperature
    data:
      temperature: 20.0
  # Set dew point for dry phase
  - action: number.set_value
    target:
      entity_id: number.espcure_dew_point_setpoint
    data:
      value: 12.2
mode: single
```

### HA Automation: Cannatrol Switch to Cure Phase (Day 4)

```yaml
alias: "EspCure — Cannatrol Switch to Cure Phase"
description: "Drop dew point setpoint to cure phase on day 4"
triggers:
  - trigger: numeric_state
    entity_id: number.espcure_cure_program_day
    above: 3
conditions:
  - condition: state
    entity_id: switch.espcure_dew_point_control_mode
    state: "on"
actions:
  - action: number.set_value
    target:
      entity_id: number.espcure_dew_point_setpoint
    data:
      value: 11.1
mode: single
```

### Which Protocol to Use?

| Protocol | Duration | Temp | Control mode | Best for |
|---|---|---|---|---|
| Rollitup step-down | ~18 days | 55 °F (12.8 °C) | RH % | Slow, forgiving, cold-plate condensation method |
| Cannatrol 4+4 | ~8 days | 68 °F (20.0 °C) | Dew point | Faster, closer to commercial result |

The rollitup method works better at lower temperatures where the Peltier is working harder and the cold plate actively condenses moisture. The Cannatrol method works at near-ambient temperature and relies on dew-point regulation to pace moisture loss.
