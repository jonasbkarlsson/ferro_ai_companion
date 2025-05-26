# Ferro AI Companion

[![GitHub Release][releases-shield]][releases]
[![Codecov][coverage-shield]][coverage]
[![License][license-shield]][license]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

![Icon](assets/icon.png)

The Ferro AI Companion integration will ...

## Requirements
- Home Assistant version 2024.12 or newer.
- [Ferroamp Operation Settings](https://github.com/jonasbkarlsson/ferroamp_operation_settings) integration.
- [Ferroamp MQTT Sensors](https://github.com/henricm/ha-ferroamp) integraton.

## Features
- ...

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

With the exception of Name, the above configuration items can be changed after intial configuration in Settings -> Devices & Services -> Integrations -> Ferro AI Companion -> 1 device -> Configure. To change Name, the native way to rename Integrations or Devices in Home Assistant can be used.

Additional parameters that affects how the charging will be performed are available as configuration entities. These entities can be placed in the dashboard and can be controlled using automations.

### Configuration entities

Entity | Type | Descriptions, valid value ranges and service calls
-- | -- | --

## Entities

Entity | Type | Description
-- | -- | --


## Lovelace UI

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
