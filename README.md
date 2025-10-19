# Ferro AI Companion

[![GitHub Release][releases-shield]][releases]
[![Codecov][coverage-shield]][coverage]
[![License][license-shield]][license]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

![Icon](assets/logo.png)

The Ferro AI Companion integration works on top of Ferro AI from Ferroamp. It provides observation of what Ferro AI does and possibilities to override the Ferro AI function.

It might take up to 24 hours until the integration has learned the peak shaving thresholds used by Ferro AI. After that, changes to the thresholds will be tracked continously.

## Requirements
- Home Assistant version 2024.12 or newer.
- [Ferroamp Operation Settings](https://github.com/jonasbkarlsson/ferroamp_operation_settings) integration.
- [Ferroamp MQTT Sensors](https://github.com/henricm/ha-ferroamp) integraton.

## Features
- Shows the peak shaving threshold(s) that Ferro AI is using to reduce peak power.
- Shows in which of the modes that Ferro AI is operating in.
- Can override the Ferro AI operating mode.

## Installation

### HACS
1. In Home Assistant go to HACS and search for "Ferro AI Companion". Click on "Ferro AI Companion" and then on "Download".

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jonasbkarlsson&repository=ferro_ai_companion&category=integration)

2. In Home Assistant go to Settings -> Devices & Services -> Integrations. Click on "+ Add integration" and search for "Ferro AI Companion".

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ferro_ai_companion)

### Manual

1. Using the tool of choice open the folder for your Home Assistant configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` folder there, you need to create it.
3. In the `custom_components` folder create a new folder called `ferro_ai_companion`.
4. Download _all_ the files from the `custom_components/ferro_ai_companion/` folder in this repository.
5. Place the files you downloaded in the new folder you created.
6. Restart Home Assistant.
7. In Home Assistant go to Settings -> Devices & Services -> Integrations. Click on "+ Add integration" and search for "Ferro AI Companion".

## Configuration

The configuration is done in the Home Assistant user interface.

Parameter | Required | Description
-- | -- | --
Name | Yes | The name of the instance.
Ferroamp Operation Settings entity | Yes | Any Ferroamp Operation Settings entity.
Ferroamp MQTT Sensor entity | Yes | Any Ferroamp MQTT Sensor entity.
Capacity-based tariff | Yes | Can be `None`, `Same during day and night` or `Different for day and night`. Should be set to the same value as configured for Ferro AI.

The integration will automatically provide values for some of these parameters. If there are more than one instance of any of the two required integrations, make sure the provided entities are from the correct instance.

With the exception of Name, the above configuration items can be changed after intial configuration in Settings -> Devices & Services -> Integrations -> Ferro AI Companion -> 1 device -> Configure. To change Name, the native way to rename Integrations or Devices in Home Assistant can be used.

## Entities

Entities other than Sensor can be set using relevant service calls, `select.select_option` and `switch.turn_on`/`switch.turn_off`.

Entity | Type | Description
-- | -- | --
`sensor.ferro_ai_companion_energyhub_mode` | Sensor | Operation mode used by EnergyHub. Will be the same as the `Ferro AI mode` if `Companion mode` is set to `Auto`. Can be `Peak shaving with charging`, `Peak shaving with selling`, `Self consumption`, `Buy` or `Sell`.
`sensor.ferro_ai_companion_ferro_ai_mode` | Sensor | Operation mode choosen by Ferro AI. Can be `Peak shaving with charging`, `Peak shaving with selling`, `Self consumption`, `Buy` or `Sell`.
`sensor.ferro_ai_companion_peak_shaving_target` | Sensor | The peak shaving threshold used by Ferro AI to reduce peak power. If Ferro AI is configured to reduce peak power to two different levels (one during day, one during night), this sensor will show the day threshold.
`sensor.ferro_ai_companion_secondary_peak_shaving_target` | Sensor | If Ferro AI is configured to reduce peak power to two different levels (one during day, one during night), this sensor will show the night threshold.
`sensor.ferro_ai_companion_current_peak_shaving_target` | Sensor | The current peak shaving target, if capacity-based tariffs are configured. Useful if Ferro AI is configured to reduce peak power to two different levels.
`switch.select.ferro_ai_companion_companion_mode` | Select | If set to `Auto`, Ferro AI will control EnergyHub mode. Override by setting to `Peak shaving with charging`, `Peak shaving with selling`, `Self consumption`, `Buy` or `Sell`.
`switch.ferro_ai_companion_avoid_selling` | Switch | When companion mode is set to `Auto`, turning this switch on will avoid selling. If Ferro AI use `Peak shaving with selling` or `Sell`, it will be override with `Peak shaving with charging`.

To set `switch.select.ferro_ai_companion_companion_mode` in automations, use the options `auto`, `peak_charge`, `peak_sell`, `self`, `buy` and `sell`.

## Modes
### Peak shaving with charging
Ferro AI: Awaiting discharge. The battery is in standby, reserving energy for upcoming events.

Peak shaving using the current peak shaving target. Excess solar power is used to charge the battery.
### Peak shaving with selling
Ferro AI: Waiting to charge. Waiting for lower electricity price before charging the battery with solar power.

Peak shaving using the current peak shaving target. Excess solar power is being sold.
### Self consumption
Ferro AI: Maximum self consumption. The battery charges when there is excess solar power and discharges to cover self consumption.

Maximum self consumption.
### Buy
Ferro AI: Charging from the grid. Preparing the battery for coming activities.

Maximum import from grid, without exceeding the current peak shaving target.
### Sell
Ferro AI: Discharging. High electricity prices and solar power on the way. The battery discharges.

Maximum export to the grid.

## Notes

When this integration overrides the Ferro AI mode, it sets the discharge and charge thresholds to values which are 1 W higher than the values used by Ferro AI, in order to be be able to detect changes in the Ferro AI mode. For example, if Ferro AI would set the discharge threshold to 0.0 for a certain mode, this integration will set it to 1.0.

Also, if `switch.select.ferro_ai_companion_companion_mode` is set to `Buy`, the charge threshold will be set 200 W lower than the current peak shaving target. If `Capacity-based tariff` is set to `Different for day and night`, the `sensor.ferro_ai_companion_secondary_peak_shaving_target` value minus 200 W will be used between 22:00 and 06:00.

[ferro_ai_companion]: https://github.com/jonasbkarlsson/ferro_ai_companion
[releases-shield]: https://img.shields.io/github/v/release/jonasbkarlsson/ferro_ai_companion?style=for-the-badge
[releases]: https://github.com/jonasbkarlsson/ferro_ai_companion/releases
[coverage-shield]: https://img.shields.io/codecov/c/gh/jonasbkarlsson/ferro_ai_companion?style=for-the-badge&logo=codecov
[coverage]: https://app.codecov.io/gh/jonasbkarlsson/ferro_ai_companion
[license-shield]: https://img.shields.io/github/license/jonasbkarlsson/ferro_ai_companion?style=for-the-badge
[license]: https://github.com/jonasbkarlsson/ferro_ai_companion/blob/main/LICENSE
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Jonas%20Karlsson%20@jonasbkarlsson-41BDF5.svg?style=for-the-badge
[user_profile]: https://github.com/jonasbkarlsson
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-FFDD00.svg?style=for-the-badge&logo=buymeacoffee
[buymecoffee]: https://www.buymeacoffee.com/jonasbkarlsson
