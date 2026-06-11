# Cure Programs

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
