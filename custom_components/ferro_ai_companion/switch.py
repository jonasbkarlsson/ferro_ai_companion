"""Switch platform for Ferro AI Companion."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.restore_state import RestoreEntity

from custom_components.ferro_ai_companion.helpers.general import get_parameter

from .const import (
    CONF_SOLAR_EV_CHARGING_ENABLED,
    DOMAIN,
    ENTITY_KEY_AVOID_BATTERY_USAGE_SWITCH,
    ENTITY_KEY_AVOID_IMPORT_SWITCH,
    ENTITY_KEY_EV_CONNECTED_SWITCH,
    ENTITY_KEY_FORCE_BUYING_SWITCH,
    ENTITY_KEY_FORCE_SELLING_SWITCH,
    ICON,
    ICON_CONNECTION,
    SWITCH,
)
from .coordinator import FerroAICompanionCoordinator
from .entity import FerroAICompanionEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_devices
):  # pylint: disable=unused-argument
    """Setup switch platform."""
    _LOGGER.debug("FerroAICompanion.switch.py")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    switches = []
    if get_parameter(entry, CONF_SOLAR_EV_CHARGING_ENABLED, False):
        switches.append(FerroAICompanionSwitchEVConnected(entry, coordinator))
        switches.append(FerroAICompanionSwitchAvoidImport(entry, coordinator))
        switches.append(FerroAICompanionSwitchAvoidBatteryUsage(entry, coordinator))
        switches.append(FerroAICompanionSwitchForceBuying(entry, coordinator))
        switches.append(FerroAICompanionSwitchForceSelling(entry, coordinator))
    async_add_devices(switches)


# pylint: disable=abstract-method
class FerroAICompanionSwitch(FerroAICompanionEntity, SwitchEntity, RestoreEntity):
    """Ferro AI Companion switch class."""

    def __init__(self, entry, coordinator: FerroAICompanionCoordinator):
        _LOGGER.debug("FerroAICompanionSwitch.__init__()")
        super().__init__(entry)
        self.coordinator = coordinator
        id_name = self._entity_key.replace("_", "").lower()
        self._attr_unique_id = ".".join([entry.entry_id, SWITCH, id_name])
        self.set_entity_id(SWITCH, self._entity_key)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        restored: State = await self.async_get_last_state()
        if restored is not None:
            if restored.state == STATE_ON:
                await self.async_turn_on()
            else:
                await self.async_turn_off()


class FerroAICompanionSwitchEVConnected(FerroAICompanionSwitch):
    """Ferro AI Companion EV Connected switch class."""

    _entity_key = ENTITY_KEY_EV_CONNECTED_SWITCH
    _attr_icon = ICON_CONNECTION

    def __init__(self, entry, coordinator: FerroAICompanionCoordinator):
        _LOGGER.debug("FerroAICompanionSwitchEVConnected.__init__()")
        super().__init__(entry, coordinator)
        if self.is_on is None:
            self._attr_is_on = False
            self.update_ha_state()
        self.coordinator.switch_ev_connected = self.is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await super().async_turn_on(**kwargs)
        await self.coordinator.switch_ev_connected_update(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await super().async_turn_off(**kwargs)
        await self.coordinator.switch_ev_connected_update(False)


class FerroAICompanionSwitchAvoidImport(FerroAICompanionSwitch):
    """Ferro AI Companion Avoid Import switch class."""

    _entity_key = ENTITY_KEY_AVOID_IMPORT_SWITCH
    _attr_icon = ICON

    def __init__(self, entry, coordinator: FerroAICompanionCoordinator):
        _LOGGER.debug("FerroAICompanionSwitchAvoidImport.__init__()")
        super().__init__(entry, coordinator)
        if self.is_on is None:
            self._attr_is_on = False
            self.update_ha_state()
        self.coordinator.switch_avoid_import = self.is_on
        self.coordinator.switch_avoid_import_unique_id = self._attr_unique_id

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await super().async_turn_on(**kwargs)
        await self.coordinator.switch_avoid_import_update(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await super().async_turn_off(**kwargs)
        await self.coordinator.switch_avoid_import_update(False)


class FerroAICompanionSwitchAvoidBatteryUsage(FerroAICompanionSwitch):
    """Ferro AI Companion Avoid Battery Usage switch class."""

    _entity_key = ENTITY_KEY_AVOID_BATTERY_USAGE_SWITCH
    _attr_icon = ICON

    def __init__(self, entry, coordinator: FerroAICompanionCoordinator):
        _LOGGER.debug("FerroAICompanionSwitchAvoidBatteryUsage.__init__()")
        super().__init__(entry, coordinator)
        if self.is_on is None:
            self._attr_is_on = False
            self.update_ha_state()
        self.coordinator.switch_avoid_battery_usage = self.is_on
        self.coordinator.switch_avoid_battery_usage_unique_id = self._attr_unique_id

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await super().async_turn_on(**kwargs)
        await self.coordinator.switch_avoid_battery_usage_update(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await super().async_turn_off(**kwargs)
        await self.coordinator.switch_avoid_battery_usage_update(False)


class FerroAICompanionSwitchForceBuying(FerroAICompanionSwitch):
    """Ferro AI Companion Force Buying switch class."""

    _entity_key = ENTITY_KEY_FORCE_BUYING_SWITCH
    _attr_icon = ICON

    def __init__(self, entry, coordinator: FerroAICompanionCoordinator):
        _LOGGER.debug("FerroAICompanionSwitchForceBuying.__init__()")
        super().__init__(entry, coordinator)
        if self.is_on is None:
            self._attr_is_on = False
            self.update_ha_state()
        self.coordinator.switch_force_buying = self.is_on
        self.coordinator.switch_force_buying_unique_id = self._attr_unique_id

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await super().async_turn_on(**kwargs)
        await self.coordinator.switch_force_buying_update(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await super().async_turn_off(**kwargs)
        await self.coordinator.switch_force_buying_update(False)


class FerroAICompanionSwitchForceSelling(FerroAICompanionSwitch):
    """Ferro AI Companion Force Selling switch class."""

    _entity_key = ENTITY_KEY_FORCE_SELLING_SWITCH
    _attr_icon = ICON

    def __init__(self, entry, coordinator: FerroAICompanionCoordinator):
        _LOGGER.debug("FerroAICompanionSwitchForceSelling.__init__()")
        super().__init__(entry, coordinator)
        if self.is_on is None:
            self._attr_is_on = False
            self.update_ha_state()
        self.coordinator.switch_force_selling = self.is_on
        self.coordinator.switch_force_selling_unique_id = self._attr_unique_id

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await super().async_turn_on(**kwargs)
        await self.coordinator.switch_force_selling_update(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await super().async_turn_off(**kwargs)
        await self.coordinator.switch_force_selling_update(False)
