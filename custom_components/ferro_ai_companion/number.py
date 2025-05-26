"""Number platform for Ferro AI Companion."""

import logging
from typing import Union

from homeassistant.components.number import (
    RestoreNumber,
    NumberExtraStoredData,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory

from custom_components.ferro_ai_companion.helpers.general import get_parameter

from .const import (
    CONF_SOLAR_EV_CHARGING_ENABLED,
    DOMAIN,
    ENTITY_KEY_CONF_ASSUMED_HOUSE_CONSUMPTION_NUMBER,
    ENTITY_KEY_CONF_MAX_CHARGING_CURRENT_NUMBER,
    ENTITY_KEY_CONF_MIN_CHARGING_CURRENT_NUMBER,
    NUMBER,
)
from .coordinator import FerroAICompanionCoordinator
from .entity import FerroAICompanionEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_devices
):  # pylint: disable=unused-argument
    """Setup number platform."""
    _LOGGER.debug("FerroAICompanion.number.py")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    numbers = []
    if get_parameter(entry, CONF_SOLAR_EV_CHARGING_ENABLED, False):
        numbers.append(FerroAICompanionNumberMaxChargingCurrent(entry, coordinator))
        numbers.append(FerroAICompanionNumberMinChargingCurrent(entry, coordinator))
        numbers.append(
            FerroAICompanionNumberAssumedHouseConsumption(entry, coordinator)
        )
    async_add_devices(numbers)


# pylint: disable=abstract-method
class FerroAICompanionNumber(FerroAICompanionEntity, RestoreNumber):
    """Ferro AI Companion number class."""

    # To support HA 2022.7
    _attr_native_value: Union[float, None] = None  # Using Union to support Python 3.9

    def __init__(self, entry, coordinator: FerroAICompanionCoordinator):
        _LOGGER.debug("FerroAICompanionNumber.__init__()")
        super().__init__(entry)
        self.coordinator = coordinator
        id_name = self._entity_key.replace("_", "").lower()
        self._attr_unique_id = ".".join([entry.entry_id, NUMBER, id_name])
        self.set_entity_id(NUMBER, self._entity_key)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        self._attr_native_value = value

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        _LOGGER.debug("FerroAICompanionNumber.async_added_to_hass()")
        restored: NumberExtraStoredData = await self.async_get_last_number_data()
        if restored is not None:
            await self.async_set_native_value(restored.native_value)
            _LOGGER.debug(
                "FerroAICompanionNumber.async_added_to_hass() %s",
                self._attr_native_value,
            )


class FerroAICompanionNumberMaxChargingCurrent(FerroAICompanionNumber):
    """Ferro AI Companion maximum charging current number class."""

    _entity_key = ENTITY_KEY_CONF_MAX_CHARGING_CURRENT_NUMBER
    #    _attr_icon = ICON_BATTERY_50
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 1.0
    _attr_native_max_value = 32.0
    _attr_native_step = 1.0
    _attr_native_unit_of_measurement = "A"

    def __init__(self, entry, coordinator: FerroAICompanionCoordinator):
        _LOGGER.debug("FerroAICompanionNumberMaxChargingCurrent.__init__()")
        super().__init__(entry, coordinator)
        if self.value is None:
            self._attr_native_value = 16.0
            self.update_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        old_value = self._attr_native_value
        await super().async_set_native_value(value)
        self.coordinator.max_charging_current = value
        await self.coordinator.entity_changed(self._entity_key, old_value, value)


class FerroAICompanionNumberMinChargingCurrent(FerroAICompanionNumber):
    """Ferro AI Companion minimum charging current number class."""

    _entity_key = ENTITY_KEY_CONF_MIN_CHARGING_CURRENT_NUMBER
    #    _attr_icon = ICON_BATTERY_50
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 1.0
    _attr_native_max_value = 32.0
    _attr_native_step = 1.0
    _attr_native_unit_of_measurement = "A"

    def __init__(self, entry, coordinator: FerroAICompanionCoordinator):
        _LOGGER.debug("FerroAICompanionNumberMinChargingCurrent.__init__()")
        super().__init__(entry, coordinator)
        if self.value is None:
            self._attr_native_value = 6.0
            self.update_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        old_value = self._attr_native_value
        await super().async_set_native_value(value)
        self.coordinator.min_charging_current = value
        await self.coordinator.entity_changed(self._entity_key, old_value, value)


class FerroAICompanionNumberAssumedHouseConsumption(FerroAICompanionNumber):
    """Ferro AI Companion assumed house consumption number class."""

    _entity_key = ENTITY_KEY_CONF_ASSUMED_HOUSE_CONSUMPTION_NUMBER
    #    _attr_icon = ICON_BATTERY_50
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = -100000.0
    _attr_native_max_value = 100000.0
    _attr_native_step = 100.0
    _attr_native_unit_of_measurement = "W"

    def __init__(self, entry, coordinator: FerroAICompanionCoordinator):
        _LOGGER.debug("FerroAICompanionNumberAssumedHouseConsumption.__init__()")
        super().__init__(entry, coordinator)
        if self.value is None:
            self._attr_native_value = 0.0
            self.update_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        old_value = self._attr_native_value
        await super().async_set_native_value(value)
        self.coordinator.assumed_house_consumption = value
        await self.coordinator.entity_changed(self._entity_key, old_value, value)
