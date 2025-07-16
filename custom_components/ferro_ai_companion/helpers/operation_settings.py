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
from homeassistant.exceptions import ServiceNotFound
from homeassistant.helpers.entity_registry import (
    RegistryEntry,
    async_get as async_entity_registry_get,
)
from homeassistant.helpers.entity_registry import (
    EntityRegistry,
)


from ..const import (
    MODE_BUY,
    MODE_PEAK_CHARGE,
    MODE_PEAK_SELL,
    MODE_SELF,
    MODE_SELL,
    OVERRIDE_OFFSET,
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

        self.override_active = False
        self.original_discharge_threshold_w = 0
        self.original_charge_threshold_w = 0

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

        try:
            await self._hass.services.async_call(
                domain="button",
                service="press",
                target={"entity_id": self._button_get_data},
            )
        except ServiceNotFound as e:
            _LOGGER.debug("Service not found: %s", e)
            # Could happen after HA restart if the button entity is not yet available
            await asyncio.sleep(5)  # Wait a while and try again
            await self._hass.services.async_call(
                domain="button",
                service="press",
                target={"entity_id": self._button_get_data},
            )

        await asyncio.sleep(4)  # Wait for the data to be fetched

        try:
            discharge_threshold_w = float(
                self._hass.states.get(self._number_discharge_threshold).state
            )
            charge_threshold_w = float(
                self._hass.states.get(self._number_charge_threshold).state
            )
            max_soc = float(self._hass.states.get(self._number_max_soc).state)
            if max_soc > 0.0:
                self.max_soc = max_soc
            if self.override_active:
                # If override is active and the threshold values have been changed,
                # update the original values and restore the overridden thresholds.
                if (
                    discharge_threshold_w != self.discharge_threshold_w
                    or charge_threshold_w != self.charge_threshold_w
                ):
                    self.original_discharge_threshold_w = discharge_threshold_w
                    self.original_charge_threshold_w = charge_threshold_w
                    # Restore the overridden thresholds
                    await self.update_thresholds()
            else:
                # If override is not active, update both sets of values
                self.discharge_threshold_w = discharge_threshold_w
                self.charge_threshold_w = charge_threshold_w
                self.original_discharge_threshold_w = discharge_threshold_w
                self.original_charge_threshold_w = charge_threshold_w

        except (ValueError, TypeError) as e:
            _LOGGER.error("Failed to fetch operation settings data: %s", e)

    async def override(self, mode: str, peak_shaving_threshold: float) -> None:
        """Override the operation settings."""

        _LOGGER.debug("Fetching data.")
        await self.fetch_all_data()

        self.override_active = True

        if mode == MODE_SELF:
            self.discharge_threshold_w = 0
            self.charge_threshold_w = 0
        if mode == MODE_PEAK_CHARGE:
            self.discharge_threshold_w = peak_shaving_threshold
            self.charge_threshold_w = 0
        if mode == MODE_PEAK_SELL:
            self.discharge_threshold_w = peak_shaving_threshold
            self.charge_threshold_w = -100000.0
        if mode == MODE_BUY:
            if peak_shaving_threshold == 0:
                # If the peak shaving threshold has not been found yet, use 1000 W
                self.discharge_threshold_w = 1000
                self.charge_threshold_w = 1000
            else:
                self.discharge_threshold_w = peak_shaving_threshold
                self.charge_threshold_w = peak_shaving_threshold
        if mode == MODE_SELL:
            self.discharge_threshold_w = -100000.0
            self.charge_threshold_w = -100000.0

        # Apply the override offset to the thresholds
        # to ensure they are not equal to the original values
        self.discharge_threshold_w += OVERRIDE_OFFSET
        self.charge_threshold_w += OVERRIDE_OFFSET

        await self.update_thresholds()

    async def stop_override(self) -> None:
        """Stop the override of operation settings."""

        _LOGGER.debug("Fetching data.")
        await self.fetch_all_data()

        self.override_active = False
        _LOGGER.debug("Stopping override.")

        # Restore the original thresholds
        self.discharge_threshold_w = self.original_discharge_threshold_w
        self.charge_threshold_w = self.original_charge_threshold_w
        await self.update_thresholds()

    async def update_thresholds(self) -> None:
        """Update the thresholds."""
        _LOGGER.debug("Updating thresholds.")
        _LOGGER.debug("self.discharge_threshold_w = %s", self.discharge_threshold_w)
        _LOGGER.debug("self.charge_threshold_w = %s", self.charge_threshold_w)

        await self._hass.services.async_call(
            domain="number",
            service="set_value",
            service_data={"value": self.discharge_threshold_w},
            target={"entity_id": self._number_discharge_threshold},
        )
        await self._hass.services.async_call(
            domain="number",
            service="set_value",
            service_data={"value": self.charge_threshold_w},
            target={"entity_id": self._number_charge_threshold},
        )
        await self._hass.services.async_call(
            domain="button",
            service="press",
            target={"entity_id": self._button_update},
        )

    async def get_mode(self) -> str:
        """Get the current mode."""
        if self.override_active:
            # If override is active, remove the offset
            return await self.determine_mode(
                self.discharge_threshold_w - OVERRIDE_OFFSET,
                self.charge_threshold_w - OVERRIDE_OFFSET,
            )
        else:
            # If override is not active
            return await self.determine_mode(
                self.discharge_threshold_w,
                self.charge_threshold_w,
            )

    async def get_original_mode(self) -> str:
        """Get the original mode."""
        return await self.determine_mode(
            self.original_discharge_threshold_w,
            self.original_charge_threshold_w,
        )

    async def determine_mode(
        self, discharge_threshold_w: float, charge_threshold_w: float
    ) -> str:
        """Determine the mode."""
        # discharge_threshold_w is always equal or larger than charge_threshold_w
        if discharge_threshold_w > 10 and charge_threshold_w in list(range(10)):
            return MODE_PEAK_CHARGE
        elif discharge_threshold_w > 10 and charge_threshold_w > 10:
            return MODE_BUY
        elif discharge_threshold_w > 10 and charge_threshold_w < 0:
            return MODE_PEAK_SELL
        elif discharge_threshold_w < 0 and charge_threshold_w < 0:
            return MODE_SELL
        else:
            # discharge_threshold_w in list(range(10)) and charge_threshold_w in list(range(10))
            # discharge_threshold_w in list(range(10)) and charge_threshold_w < 0
            return MODE_SELF
