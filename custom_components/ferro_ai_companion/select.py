"""Select platform for EV Smart Charging."""

import logging
from typing import Union

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DOMAIN,
    ENTITY_KEY_OVERRIDE_MODE_SELECT,
    ICON_LIST,
    MODE_AUTO,
    OVERRIDE_MODES,
    SELECT,
)
from .coordinator import FerroAICompanionCoordinator
from .entity import FerroAICompanionEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_devices
):  # pylint: disable=unused-argument
    """Setup select platform."""
    _LOGGER.debug("EVSmartCharging.select.py")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    selects = []
    selects.append(FerroAICompanionSelectOverrideMode(entry, coordinator))
    async_add_devices(selects)


class FerroAICompanionSelect(FerroAICompanionEntity, SelectEntity, RestoreEntity):
    """EV Smart Charging switch class."""

    _attr_current_option: Union[str, None] = None  # Using Union to support Python 3.9

    def __init__(self, entry, coordinator: FerroAICompanionCoordinator):
        _LOGGER.debug("FerroAICompanionSelect.__init__()")
        super().__init__(entry)
        self.coordinator = coordinator
        id_name = self._entity_key.replace("_", "").lower()
        self._attr_unique_id = ".".join([entry.entry_id, SELECT, id_name])
        self.set_entity_id(SELECT, self._entity_key)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        restored: State = await self.async_get_last_state()
        if restored is not None:
            await self.async_select_option(restored.state)

    def select_option(self, option: str) -> None:
        """Dummy method to satisfy the base class."""
        return None


class FerroAICompanionSelectOverrideMode(FerroAICompanionSelect):
    """EV Smart Charging start_quarter select class."""

    _entity_key = ENTITY_KEY_OVERRIDE_MODE_SELECT
    _attr_icon = ICON_LIST
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = OVERRIDE_MODES

    def __init__(self, entry, coordinator: FerroAICompanionCoordinator):
        _LOGGER.debug("FerroAICompanionSelectReadyQuarter.__init__()")
        super().__init__(entry, coordinator)
        if self.state is None:
            self._attr_current_option = MODE_AUTO
            self.update_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        old_value = self.current_option
        self._valid_option_or_raise(option)
        await super().async_select_option(option)
        if self.state:
            await self.coordinator.generate_event(
                self._entity_key, old_value, self.current_option
            )
