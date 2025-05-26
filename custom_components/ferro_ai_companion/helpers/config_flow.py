"""Helpers for config_flow"""

from collections import UserDict
import logging
from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get as async_device_registry_get
from homeassistant.helpers.device_registry import DeviceRegistry
from homeassistant.helpers.entity_registry import async_get as async_entity_registry_get
from homeassistant.helpers.entity_registry import (
    EntityRegistry,
    RegistryEntry,
)

from custom_components.ferro_ai_companion.helpers.general import Validator

# from custom_components.ferro_ai_companion.helpers.price_adaptor import PriceAdaptor

# pylint: disable=relative-beyond-top-level
from ..const import (
    CONF_EV_SOC_SENSOR,
    CONF_EV_TARGET_SOC_SENSOR,
    CONF_SETTINGS_ENTITY,
    DOMAIN,
    NAME,
    PLATFORM_FERROAMP,
    PLATFORM_FERROAMP_OPERATION_SETTINGS,
    PLATFORM_FORECAST_SOLAR,
    PLATFORM_VW,
)

_LOGGER = logging.getLogger(__name__)


class FlowValidator:
    """Validator of flows"""

    @staticmethod
    def validate_step_user(
        hass: HomeAssistant, user_input: dict[str, Any]
    ) -> list[str]:
        """Validate step_user"""

        # TODO: Add more validation.

        # Validate Ferroamp Operation Settings entity
        user_input[CONF_SETTINGS_ENTITY] = user_input[CONF_SETTINGS_ENTITY].strip()
        if len(user_input[CONF_SETTINGS_ENTITY]) > 0:
            entity = hass.states.get(user_input[CONF_SETTINGS_ENTITY])
            if entity is None:
                return ("base", "setting_entity_not_found")

            entity_registry: EntityRegistry = async_entity_registry_get(hass)
            registry_entries: UserDict[str, RegistryEntry] = (
                entity_registry.entities.items()
            )
            platform = None
            for entry in registry_entries:
                if entry[1].entity_id == entity.entity_id:
                    platform = entry[1].platform
                    break

            if platform != PLATFORM_FERROAMP_OPERATION_SETTINGS:
                return ("base", "setting_entity_not_found")

        return None

    @staticmethod
    def validate_step_solar(
        hass: HomeAssistant, user_input: dict[str, Any]
    ) -> list[str]:
        """Validate step_solar"""

        # TODO: Add more validation.

        # Validate EV SOC entity
        entity = hass.states.get(user_input[CONF_EV_SOC_SENSOR])
        if entity is None:
            return ("base", "ev_soc_not_found")
        if not Validator.is_float(entity.state):
            _LOGGER.debug("EV SOC state is not float")
            return ("base", "ev_soc_invalid_data")
        if not 0.0 <= float(entity.state) <= 100.0:
            _LOGGER.debug("EV SOC state is between 0 and 100")
            return ("base", "ev_soc_invalid_data")

        # Validate EV Target SOC entity
        user_input[CONF_EV_TARGET_SOC_SENSOR] = user_input[
            CONF_EV_TARGET_SOC_SENSOR
        ].strip()
        if len(user_input[CONF_EV_TARGET_SOC_SENSOR]) > 0:
            entity = hass.states.get(user_input[CONF_EV_TARGET_SOC_SENSOR])
            if entity is None:
                return ("base", "ev_target_soc_not_found")
            if not Validator.is_float(entity.state):
                _LOGGER.debug("EV Target SOC state is not float")
                return ("base", "ev_target_soc_invalid_data")
            if not 0.0 <= float(entity.state) <= 100.0:
                _LOGGER.debug("EV Target SOC state is between 0 and 100")
                return ("base", "ev_target_soc_invalid_data")

        return None


class FindEntity:
    """Find entities"""

    @staticmethod
    def find_vw_soc_sensor(hass: HomeAssistant) -> str:
        """Search for Volkswagen SOC sensor"""
        entity_registry: EntityRegistry = async_entity_registry_get(hass)
        registry_entries: UserDict[str, RegistryEntry] = (
            entity_registry.entities.items()
        )
        for entry in registry_entries:
            if entry[1].platform == PLATFORM_VW:
                entity_id = entry[1].entity_id
                if "state_of_charge" in entity_id:
                    if not "target_state_of_charge" in entity_id:
                        return entity_id
        return ""

    @staticmethod
    def find_vw_target_soc_sensor(hass: HomeAssistant) -> str:
        """Search for Volkswagen Target SOC sensor"""
        entity_registry: EntityRegistry = async_entity_registry_get(hass)
        registry_entries: UserDict[str, RegistryEntry] = (
            entity_registry.entities.items()
        )
        for entry in registry_entries:
            if entry[1].platform == PLATFORM_VW:
                entity_id = entry[1].entity_id
                if "target_state_of_charge" in entity_id:
                    return entity_id
        return ""

    @staticmethod
    def find_setting_entity(hass: HomeAssistant) -> str:
        """Find Ferroamp Operation Settings entity"""
        entity_registry: EntityRegistry = async_entity_registry_get(hass)
        registry_entries: UserDict[str, RegistryEntry] = (
            entity_registry.entities.items()
        )
        for entry in registry_entries:
            if entry[1].platform == PLATFORM_FERROAMP_OPERATION_SETTINGS:
                entity_id = entry[1].entity_id
                if entity_id.startswith("number"):  # Get the first number entity
                    return entity_id
        return ""

    @staticmethod
    def find_mqtt_entity(hass: HomeAssistant) -> str:
        """Find Ferroamp MQTT Sensor entity"""
        entity_registry: EntityRegistry = async_entity_registry_get(hass)
        registry_entries: UserDict[str, RegistryEntry] = (
            entity_registry.entities.items()
        )
        for entry in registry_entries:
            if entry[1].platform == PLATFORM_FERROAMP:
                entity_id = entry[1].entity_id
                if entity_id.startswith("sensor"):  # Get the first sensor entity
                    return entity_id
        return ""

    @staticmethod
    def find_forecast_entity(hass: HomeAssistant) -> str:
        """Find Forecast.Solar entity"""
        entity_registry: EntityRegistry = async_entity_registry_get(hass)
        registry_entries: UserDict[str, RegistryEntry] = (
            entity_registry.entities.items()
        )
        for entry in registry_entries:
            if entry[1].platform == PLATFORM_FORECAST_SOLAR:
                entity_id = entry[1].entity_id
                if (
                    entry[1].original_name
                    == "Estimated energy production - remaining today"
                ):
                    return entity_id
        return ""


class DeviceNameCreator:
    """Class that creates the name of the new device"""

    @staticmethod
    def create(hass: HomeAssistant) -> str:
        """Create device name"""
        device_registry: DeviceRegistry = async_device_registry_get(hass)
        devices = device_registry.devices
        # Find existing Ferro AI Companion devices
        ev_devices = []
        for device in devices:
            for item in devices[device].identifiers:
                if item[0] == DOMAIN:
                    ev_devices.append(device)
        # If this is the first device. just return NAME
        if len(ev_devices) == 0:
            return NAME
        # Find the highest number at the end of the name
        higest = 1
        for device in ev_devices:
            device_name: str = devices[device].name
            if device_name == NAME:
                pass
            else:
                try:
                    device_number = int(device_name[len(NAME) :])
                    if device_number > higest:
                        higest = device_number
                except ValueError:
                    pass
        # Add ONE to the highest value and append after NAME
        return f"{NAME} {higest+1}"
