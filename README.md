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
- Shows in which of the four modes that Ferro AI is operating in.
- Can overide the Ferro AI operating mode.

## Installation

### HACS
1. In Home Assistant go to HACS -> Integrations. Click on the three dots in the upper-right corner and select "Custom repositories". Paste the URL [ferro_ai_companion](https://github.com/jonasbkarlsson/ferro_ai_companion) into the Repository field. In Category select Integration. Click on ADD.
2. In Home Assistant go to HACS -> Integrations. Click on "+ Explore & Download Repositories" and search for "Ferro AI Companion".
3. In Home Assistant go to Settings -> Devices & Services -> Integrations. Click on "+ Add integration" and search for "Ferro AI Companion".

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
Ferroamp Operation Settings entity | Yes | Any Any Ferroamp Operation Settings entity.
Ferroamp MQTT Sensor entity | Yes | Any Ferroamp MQTT Sensor entity.

With the exception of Name, the above configuration items can be changed after intial configuration in Settings -> Devices & Services -> Integrations -> Ferro AI Companion -> 1 device -> Configure. To change Name, the native way to rename Integrations or Devices in Home Assistant can be used.

## Entities

Entity | Type | Description
-- | -- | --
`sensor.ferro_ai_companion_energyhub_mode` | Sensor | Operation mode used by EnergyHub. Will be the same as the `Ferro AI mode` if `Companion mode` is set to `Auto`. Can be `Peak shaving`, `Self consumption`, `Buy` or `Sell`.
`sensor.ferro_ai_companion_ferro_ai_mode` | Sensor | Operation mode choosen by Ferro AI. Can be `Peak shaving`, `Self consumption`, `Buy` or `Sell`.
`sensor.ferro_ai_companion_peak_shaving_target` | Sensor | The peak shaving threshold used by Ferro AI to reduce peak power.
`sensor.ferro_ai_companion_secondary_peak_shaving_target` | Sensor | If Ferro AI is configured to reduce peak power to two different levels (one during day, one during night), this sensor will show the night threshold.
`switch.select.ferro_ai_companion_companion_mode` | Select | If set to `Auto`, Ferro AI will control EnergyHub mode. Override by setting to `Peak shaving`, `Self consumption`, `Buy` or `Sell`.

[ferro_ai_companion]: https://github.com/jonasbkarlsson/ferro_ai_companion
[releases-shield]: https://img.shields.io/github/v/release/jonasbkarlsson/ferro_ai_companion?style=for-the-badge
[releases]: https://github.com/jonasbkarlsson/ferro_ai_companion/releases
[coverage-shield]: https://img.shields.io/codecov/c/gh/jonasbkarlsson/ferro_ai_companion?style=for-the-badge&logo=codecov
[coverage]: https://app.codecov.io/gh/jonasbkarlsson/ferro_ai_companion
[license-shield]: https://img.shields.io/github/license/jonasbkarlsson/ferro_ai_companion?style=for-the-badge
[license]: https://github.com/jonasbkarlsson/ferro_ai_companion/blob/main/LICENSE
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Jonas%20Karlsson%20@jonasbkarlsson-41BDF5.svg?style=for-the-badge
[user_profile]: https://github.com/jonasbkarlsson
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-FFDD00.svg?style=for-the-badge&logo=buymeacoffee
[buymecoffee]: https://www.buymeacoffee.com/jonasbkarlsson
