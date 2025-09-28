"""Sensor platform for Ferro AI Companion."""

import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.core import HomeAssistant

from custom_components.ferro_ai_companion.helpers.general import get_parameter


from .const import (
    CONF_SOLAR_EV_CHARGING_ENABLED,
    DOMAIN,
    ENTITY_KEY_CHARGING_CURRENT_SENSOR,
    ENTITY_KEY_MODE_SENSOR,
    ENTITY_KEY_ORIGINAL_MODE_SENSOR,
    ENTITY_KEY_PEAK_SHAVING_TARGET_SENSOR,
    ENTITY_KEY_SECONDARY_PEAK_SHAVING_TARGET_SENSOR,
    ENTITY_KEY_SOLAR_EV_CHARGING_SENSOR,
    FERRO_AI_MODES,
    ICON_MODE,
    ICON_POWER_TARGET,
    SENSOR,
)
from .entity import FerroAICompanionEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_devices):
    """Setup sensor platform."""
    _LOGGER.debug("FerroAICompanion.sensor.py")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []
    sensors.append(FerroAICompanionSensorMode(entry))
    sensors.append(FerroAICompanionSensorPeakShavingTarget(entry))
    sensors.append(FerroAICompanionSensorSecondaryPeakShavingTarget(entry))
    sensors.append(FerroAICompanionSensorOriginalMode(entry))
    if get_parameter(entry, CONF_SOLAR_EV_CHARGING_ENABLED, False):
        sensors.append(FerroAICompanionSensorChargingCurrent(entry))
        sensors.append(FerroAICompanionSensorSolarEVCharging(entry))
    async_add_devices(sensors)
    await coordinator.add_sensor(sensors)


class FerroAICompanionSensor(FerroAICompanionEntity, SensorEntity):
    """Ferro AI Companion sensor class."""

    def __init__(self, entry):
        _LOGGER.debug("FerroAICompanionSensor.__init__()")
        super().__init__(entry)
        id_name = self._entity_key.replace("_", "").lower()
        self._attr_unique_id = ".".join([entry.entry_id, SENSOR, id_name])
        self.set_entity_id(SENSOR, self._entity_key)

    def set(self, new_value):
        """Set new status."""
        self._attr_native_value = new_value
        self.update_ha_state()


class FerroAICompanionSensorMode(FerroAICompanionSensor):
    """Ferro AI Companion sensor class."""

    _entity_key = ENTITY_KEY_MODE_SENSOR
    _attr_icon = ICON_MODE
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = FERRO_AI_MODES

    def __init__(self, entry):
        _LOGGER.debug("FerroAICompanionSensorMode.__init__()")
        #        self._attr_native_value = MODE_UNKNOWN
        super().__init__(entry)


class FerroAICompanionSensorOriginalMode(FerroAICompanionSensor):
    """Ferro AI Companion sensor class."""

    _entity_key = ENTITY_KEY_ORIGINAL_MODE_SENSOR
    _attr_icon = ICON_MODE
    _attr_device_class = SensorDeviceClass.ENUM

    def __init__(self, entry):
        _LOGGER.debug("FerroAICompanionSensorOriginalMode.__init__()")
        #        self._attr_native_value = MODE_UNKNOWN
        super().__init__(entry)


class FerroAICompanionSensorPeakShavingTarget(FerroAICompanionSensor):
    """Ferro AI Companion sensor class."""

    _entity_key = ENTITY_KEY_PEAK_SHAVING_TARGET_SENSOR
    _attr_icon = ICON_POWER_TARGET
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "W"
    _attr_suggested_display_precision = 0

    def __init__(self, entry):
        _LOGGER.debug("FerroAICompanionSensorPeakShavingTarget.__init__()")
        #        self._attr_native_value = 0
        super().__init__(entry)


class FerroAICompanionSensorSecondaryPeakShavingTarget(FerroAICompanionSensor):
    """Ferro AI Companion sensor class."""

    _entity_key = ENTITY_KEY_SECONDARY_PEAK_SHAVING_TARGET_SENSOR
    _attr_icon = ICON_POWER_TARGET
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "W"
    _attr_suggested_display_precision = 0

    def __init__(self, entry):
        _LOGGER.debug("FerroAICompanionSensorSecondaryPeakShavingTarget.__init__()")
        #        self._attr_native_value = 0
        super().__init__(entry)


class FerroAICompanionSensorChargingCurrent(FerroAICompanionSensor):
    """Ferro AI Companion sensor class."""

    _entity_key = ENTITY_KEY_CHARGING_CURRENT_SENSOR
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = "A"

    def __init__(self, entry):
        _LOGGER.debug("FerroAICompanionSensorChargingCurrent.__init__()")
        self._attr_native_value = 0
        super().__init__(entry)


class FerroAICompanionSensorSolarEVCharging(FerroAICompanionSensor):
    """Ferro AI Companion sensor class."""

    _entity_key = ENTITY_KEY_SOLAR_EV_CHARGING_SENSOR
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [STATE_OFF, STATE_ON]

    def __init__(self, entry):
        _LOGGER.debug("FerroAICompanionSensorSolarEVCharging.__init__()")
        self._attr_native_value = STATE_OFF
        super().__init__(entry)
