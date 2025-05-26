"""Ferro AI Companion Operation Settings Helper Module.
This module provides functionality to manage and fetch operation settings"""

import asyncio
from collections import UserDict
import logging
from homeassistant.config_entries import (
    ConfigEntry,
)

from homeassistant.core import (
    HomeAssistant,
)

from homeassistant.helpers.entity_registry import (
    RegistryEntry,
    async_get as async_entity_registry_get,
)
from homeassistant.helpers.entity_registry import (
    EntityRegistry,
)

_LOGGER = logging.getLogger(__name__)


class OperationSettings:
    """Class to handle operation settings for Ferro AI Companion."""

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, entity_id: str
    ) -> None:
        """Initialize."""
        self._hass = hass
        self._config_entry = config_entry
        self._button_get_data = None
        self._button_update = None
        self._number_discharge_threshold = None
        self._number_charge_threshold = None
        self._number_charge_threshold = None
        self._number_max_soc = None  # Ferroamp Operation Settings Upper reference

        self.discharge_threshold_w = 0
        self.charge_threshold_w = 0
        self.max_soc = -1.0  # -1 means not set

        if entity_id:
            entity_registry: EntityRegistry = async_entity_registry_get(hass)
            registry_entries: UserDict[str, RegistryEntry] = (
                entity_registry.entities.items()
            )
            device_id = None
            for entry in registry_entries:
                if entry[1].entity_id == entity_id:
                    device_id = entry[1].device_id
                    break
            if device_id is not None:
                for entry in registry_entries:
                    if entry[1].device_id == device_id:
                        if entry[1].original_name == "Get data":
                            self._button_get_data = entry[1].entity_id
                        elif entry[1].original_name == "Update":
                            self._button_update = entry[1].entity_id
                        elif entry[1].original_name == "Discharge threshold":
                            self._number_discharge_threshold = entry[1].entity_id
                        elif entry[1].original_name == "Charge threshold":
                            self._number_charge_threshold = entry[1].entity_id
                        elif entry[1].original_name == "Upper reference":
                            self._number_max_soc = entry[1].entity_id

    async def fetch_all_data(self) -> None:
        """Fetch all operation settings data."""

        #        self._hass.services.call('button', 'press', {'entity_id': self.button_get_data})

        await self._hass.services.async_call(
            domain="button",
            service="press",
            target={"entity_id": self._button_get_data},
        )

        await asyncio.sleep(5)  # Wait for the data to be fetched

        try:
            discharge_threshold_w = float(
                self._hass.states.get(self._number_discharge_threshold).state
            )
            charge_threshold_w = float(
                self._hass.states.get(self._number_charge_threshold).state
            )
            max_soc = float(self._hass.states.get(self._number_max_soc).state)
            if (
                self.discharge_threshold_w != discharge_threshold_w
                or self.charge_threshold_w != charge_threshold_w
                or self.max_soc != max_soc
            ):
                self.discharge_threshold_w = discharge_threshold_w
                self.charge_threshold_w = charge_threshold_w
                self.max_soc = max_soc

        except (ValueError, TypeError) as e:
            _LOGGER.error("Failed to fetch operation settings data: %s", e)
