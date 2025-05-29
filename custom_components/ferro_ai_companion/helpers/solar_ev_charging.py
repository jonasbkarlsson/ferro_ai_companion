"""Coordinator for Ferro AI Companion"""

from collections import UserDict
from datetime import datetime
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

# from custom_components.ferro_ai_companion.helpers.price_adaptor import PriceAdaptor

from ..const import (
    CONF_SOLAR_FORECAST_TODAY_REMAINING,
)
from .general import get_parameter

_LOGGER = logging.getLogger(__name__)


class SolarEVCharging:
    """Class to handle solar EV charging for Ferro AI Companion."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        entity_id: str,
    ) -> None:
        """Initialize."""
        self._hass = hass
        self._config_entry = config_entry
        self.sensor_ferroamp_system_state_of_charge = None
        self._sensor_ferroamp_total_rated_capacity_of_all_batteries = None
        self._sensor_ferroamp_solar_power = None
        self._sensor_ferroamp_external_volatage = None
        self._sensor_remaining_solar_energy = get_parameter(
            self._config_entry, CONF_SOLAR_FORECAST_TODAY_REMAINING
        )

        self.external_voltage_v = -1.0  # -1 means not set
        self.total_rated_soc_wh = -1.0  # -1 means not set

        self.start_soc = 100.0
        self.stop_soc = 95.0

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
                        if entry[1].original_name == "System State of Charge":
                            self.sensor_ferroamp_system_state_of_charge = entry[
                                1
                            ].entity_id
                        elif (
                            entry[1].original_name
                            == "Total Rated Capacity of All Batteries"
                        ):
                            self._sensor_ferroamp_total_rated_capacity_of_all_batteries = entry[
                                1
                            ].entity_id
                        elif entry[1].original_name == "Solar Power":
                            self._sensor_ferroamp_solar_power = entry[1].entity_id
                        elif entry[1].original_name == "External Voltage":
                            self._sensor_ferroamp_external_volatage = entry[1].entity_id

    async def fetch_all_data(self) -> None:
        """Fetch all operation settings data."""

        try:
            self.external_voltage_v = (
                float(
                    self._hass.states.get(self._sensor_ferroamp_external_volatage).state
                )
                / 3
            )
            self.total_rated_soc_wh = float(
                self._hass.states.get(
                    self._sensor_ferroamp_total_rated_capacity_of_all_batteries
                ).state
            )
        except (ValueError, TypeError, AttributeError) as e:
            _LOGGER.debug("Failed to fetch EnergyHub data: %s", e)

    def set_start_stop_soc(
        self,
        remaining_solar_energy_wh: float,
        assumed_house_consumption_w: float,
        max_soc: float,
    ) -> None:
        """Set the start/stop SOC based on remaining solar energy."""

        if self.total_rated_soc_wh == -1.0:
            _LOGGER.debug(
                "self.start_soc cannot be calculated. Total rated SOC missing."
            )
            return  # Cannot calculate without total rated SOC
        if max_soc == -1.0:
            max_soc = 100.0  # Default to 100% if not set

        next_setting_str = self._hass.states.get("sensor.sun_next_setting").state
        next_setting = datetime.fromisoformat(next_setting_str)
        current_time = datetime.now(next_setting.tzinfo)
        time_difference = next_setting - current_time
        hours_until = time_difference.total_seconds() / 3600
        if hours_until < 0:
            hours_until = 0

        self.stop_soc = (
            (
                self.total_rated_soc_wh * max_soc / 100.0
                - (
                    remaining_solar_energy_wh
                    - assumed_house_consumption_w * hours_until
                )
            )
            / self.total_rated_soc_wh
            * 100.0
        )
        if self.stop_soc < 0:
            self.stop_soc = 0.0
        if self.stop_soc > (max_soc - 5):
            self.stop_soc = max_soc - 5
        self.start_soc = self.stop_soc + 5.0

        _LOGGER.debug("hours_until = %s", hours_until)
        _LOGGER.debug("self.start_soc = %s", self.start_soc)
        _LOGGER.debug("self.stop_soc = %s", self.stop_soc)

    async def solar_start_trigger(self) -> None:
        """Stop solar EV charging."""
        if self.sensor_ferroamp_system_state_of_charge:
            try:
                ferroamp_sysetem_soc = float(
                    self._hass.states.get(
                        self.sensor_ferroamp_system_state_of_charge
                    ).state
                )
                if ferroamp_sysetem_soc >= self.start_soc:
                    await self.solar_start_conditions()
            except (ValueError, TypeError, AttributeError) as e:
                _LOGGER.debug(e)

    async def solar_start_conditions(self) -> None:
        """Start solar EV charging."""
        # Trigger 1: EV Connected changed to "on"
        # Trigger 2: Every five minutes
        # Trigger 3: Ferroamp System State of Charge >= Start SOC

        _LOGGER.debug("solar_start_conditions called")

        # conditions:
        #   - condition: state
        #     entity_id: switch.ev_smart_charging_ev_connected
        #     state: "on"
        #   - condition: numeric_state
        #     entity_id: sensor.volkswagen_id_id_4_gtx_state_of_charge
        #     below: sensor.volkswagen_id_id_4_gtx_target_state_of_charge
        #   - condition: template
        #     value_template: >-
        #       {{states('sensor.ferroamp_system_state_of_charge') >=
        #       states('input_number.solar_charging_start_soc')}}
        #   - condition: state
        #     entity_id: input_boolean.solar_charging_ongoing
        #     state: "off"
        #   - condition: numeric_state
        #     entity_id: sensor.ferroamp_solar_power
        #     above: 3000
        if (
            self.sensor_ferroamp_system_state_of_charge
            and self._sensor_ferroamp_solar_power
        ):
            ferroamp_sysetem_soc = float(
                self._hass.states.get(self.sensor_ferroamp_system_state_of_charge).state
            )
            solar_power = float(
                self._hass.states.get(self._sensor_ferroamp_solar_power).state
            )
            if (
                ferroamp_sysetem_soc >= self.start_soc
                and solar_power > 3000  # Example threshold for solar power
            ):
                _LOGGER.debug("Starting solar EV charging")
                # TODO: Here you would add the logic to start the charging process
