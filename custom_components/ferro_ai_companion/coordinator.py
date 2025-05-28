"""Coordinator for Ferro AI Companion"""

import asyncio
from datetime import datetime
import logging
from random import randint
from homeassistant.config_entries import (
    ConfigEntry,
)

from homeassistant.core import (
    EventStateChangedData,
    HomeAssistant,
    callback,
    Event,
)

from homeassistant.helpers import storage
from homeassistant.helpers.device_registry import EVENT_DEVICE_REGISTRY_UPDATED
from homeassistant.helpers.device_registry import async_get as async_device_registry_get
from homeassistant.helpers.device_registry import DeviceRegistry
from homeassistant.helpers.event import (
    async_call_later,
    async_track_time_change,
    async_track_state_change_event,
)
from homeassistant.helpers.entity_registry import (
    async_get as async_entity_registry_get,
)
from homeassistant.helpers.entity_registry import (
    EntityRegistry,
    async_entries_for_config_entry,
)
from homeassistant.const import STATE_ON
from homeassistant.util import dt

from .const import (
    CONF_EV_SOC_SENSOR,
    CONF_EV_TARGET_SOC_SENSOR,
    CONF_MQTT_ENTITY,
    CONF_SETTINGS_ENTITY,
    CONF_SOLAR_EV_CHARGING_ENABLED,
    CONF_SOLAR_FORECAST_TODAY_REMAINING,
    ENTITY_KEY_AVOID_BATTERY_USAGE_SWITCH,
    ENTITY_KEY_AVOID_IMPORT_SWITCH,
    ENTITY_KEY_EV_CONNECTED_SWITCH,
    ENTITY_KEY_FORCE_BUYING_SWITCH,
    ENTITY_KEY_FORCE_SELLING_SWITCH,
    MODE_BUY,
    MODE_PEAK_SHAVING,
    MODE_SELF,
    MODE_SELL,
)
from .helpers.general import Validator, get_parameter
from .helpers.operation_settings import OperationSettings
from .helpers.solar_ev_charging import SolarEVCharging
from .sensor import (
    FerroAICompanionSensor,
    FerroAICompanionSensorMode,
    FerroAICompanionSensorChargingCurrent,
    FerroAICompanionSensorOriginalMode,
    FerroAICompanionSensorPeakShavingTarget,
    FerroAICompanionSensorSecondaryPeakShavingTarget,
    FerroAICompanionSensorSolarEVCharging,
)


_LOGGER = logging.getLogger(__name__)

STORAGE_KEY = "ferro_ai_companion.coordinator"
STORAGE_VERSION = 1


# Global lock
ferro_ai_companion_coordinator_lock = asyncio.Lock()


class FerroAICompanionCoordinator:
    """Coordinator class"""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize."""
        self.hass = hass
        self.config_entry = config_entry
        self.platforms = []
        self.listeners = []
        self.setup_timestamp = None

        self.sensor_mode = None
        self.sensor_original_mode = None
        self.sensor_peak_shaving_target = None
        self.sensor_secondary_peak_shaving_target = None
        self.sensor_charging_current = None
        self.sensor_solar_ev_charging = None

        self.switch_ev_connected = None
        self.switch_avoid_import = None
        self.switch_avoid_battery_usage = None
        self.switch_force_buying = None
        self.switch_force_selling = None

        self.solar_forecast_today_remaining_entity_id = None
        self.ev_soc_entity_id = None
        self.ev_target_soc_entity_id = None

        self.ev_soc = None
        self.ev_target_soc = None
        self.ev_soc_valid = False
        self.ev_target_soc_valid = False

        self.primary_peak_shaving_target_w = 0.0
        self.secondary_peak_shaving_target_w = 0.0

        self.min_charging_current = 6.0
        self.max_charging_current = 16.0
        self.assumed_house_consumption = 0.0

        self.data_store = storage.Store(hass, STORAGE_VERSION, STORAGE_KEY)

        self.operation_settings = OperationSettings(
            hass, config_entry, get_parameter(self.config_entry, CONF_SETTINGS_ENTITY)
        )
        self.solar_ev_charging = None
        if get_parameter(self.config_entry, CONF_SOLAR_EV_CHARGING_ENABLED, False):
            self.solar_ev_charging = SolarEVCharging(
                hass, config_entry, get_parameter(self.config_entry, CONF_MQTT_ENTITY)
            )

        # Update state once per quarter.
        # Randomize the minute and second to avoid all instances updating at the same time.
        y = randint(0, 1)
        self.listeners.append(
            async_track_time_change(
                hass,
                self.update_quarterly,
                minute=[x + y for x in [4, 19, 34, 49]],
                second=randint(0, 59),
            )
        )
        # Listen for changes to the device.
        self.listeners.append(
            hass.bus.async_listen(EVENT_DEVICE_REGISTRY_UPDATED, self.device_updated)
        )
        # Update state once after intitialization
        self.listeners.append(async_call_later(hass, 10.0, self.update_initial))

    def unsubscribe_listeners(self):
        """Unsubscribed to listeners"""
        for unsub in self.listeners:
            unsub()

    @callback
    async def device_updated(self, event: Event):  # pylint: disable=unused-argument
        """Called when device is updated"""
        _LOGGER.debug("FerroAICompanionCoordinator.device_updated()")
        if "device_id" in event.data:
            entity_registry: EntityRegistry = async_entity_registry_get(self.hass)
            all_entities = async_entries_for_config_entry(
                entity_registry, self.config_entry.entry_id
            )
            if all_entities:
                device_id = all_entities[0].device_id
                if event.data["device_id"] == device_id:
                    if "changes" in event.data:
                        if "name_by_user" in event.data["changes"]:
                            # If the device name is changed, update the integration name
                            device_registry: DeviceRegistry = async_device_registry_get(
                                self.hass
                            )
                            device = device_registry.async_get(device_id)
                            if device.name_by_user != self.config_entry.title:
                                self.hass.config_entries.async_update_entry(
                                    self.config_entry, title=device.name_by_user
                                )

    def is_during_intialization(self) -> bool:
        """Checks if the integration is being intialized"""
        # First update is done after 10 seconds, wait another 5 seconds
        # before any EV charging is started.
        now_timestamp = dt.now().timestamp()
        time_since_start = now_timestamp - self.setup_timestamp
        return time_since_start < 15

    @callback
    async def update_initial(
        self, date_time: datetime = None
    ):  # pylint: disable=unused-argument
        """Called once"""
        _LOGGER.debug("FerroAICompanionCoordinator.update_initial()")
        data = await self.data_store.async_load()
        if data:
            data = data.get(self.config_entry.entry_id)
            if data:
                self.primary_peak_shaving_target_w = data.get(
                    "primary_peak_shaving_target_w", 0.0
                )  # Default to 0 if not set
                self.secondary_peak_shaving_target_w = data.get(
                    "secondary_peak_shaving_target_w", 0.0
                )  # Default to 0 if not set
                self.sensor_peak_shaving_target.set(self.primary_peak_shaving_target_w)
                self.sensor_secondary_peak_shaving_target.set(
                    self.secondary_peak_shaving_target_w
                )

        await self.update_quarterly()

        if get_parameter(self.config_entry, CONF_SOLAR_EV_CHARGING_ENABLED, False):
            try:
                remaining_solar_energy_wh = (
                    float(
                        self.hass.states.get(
                            self.solar_forecast_today_remaining_entity_id
                        ).state
                    )
                    * 1000
                )  # Convert kWh to Wh
                self.solar_ev_charging.set_start_stop_soc(
                    remaining_solar_energy_wh,
                    self.assumed_house_consumption,
                    self.operation_settings.max_soc,
                )

            except (ValueError, TypeError) as e:
                _LOGGER.error("Failed to fetch remaining solar energy: %s", e)

    @callback
    async def update_quarterly(
        self, date_time: datetime = None
    ):  # pylint: disable=unused-argument
        """Called every quarter"""
        _LOGGER.debug("FerroAICompanionCoordinator.update_quarterly()")
        await self.operation_settings.fetch_all_data()
        if get_parameter(self.config_entry, CONF_SOLAR_EV_CHARGING_ENABLED, False):
            await self.solar_ev_charging.fetch_all_data()

        _LOGGER.debug(
            "self.operation_settings.discharge_threshold = %s",
            self.operation_settings.discharge_threshold_w,
        )
        _LOGGER.debug(
            "self.operation_settings.charge_threshold = %s",
            self.operation_settings.charge_threshold_w,
        )

        if (
            self.operation_settings.discharge_threshold_w > 0
            and self.operation_settings.charge_threshold_w == 0
        ):
            self.sensor_mode.set(MODE_PEAK_SHAVING)
            _LOGGER.debug("Mode = %s", MODE_PEAK_SHAVING)
        elif (
            self.operation_settings.charge_threshold_w > 0
            and self.operation_settings.discharge_threshold_w > 0
        ):
            self.sensor_mode.set(MODE_BUY)
            _LOGGER.debug("Mode = %s", MODE_BUY)
        elif (
            self.operation_settings.charge_threshold_w < 0
            and self.operation_settings.discharge_threshold_w < 0
        ):
            self.sensor_mode.set(MODE_SELL)
            _LOGGER.debug("Mode = %s", MODE_SELL)
        else:
            self.sensor_mode.set(MODE_SELF)
            _LOGGER.debug("Mode = %s", MODE_SELF)

        if get_parameter(self.config_entry, CONF_SOLAR_EV_CHARGING_ENABLED, False):
            if (
                self.operation_settings.discharge_threshold_w > 0
                and self.operation_settings.charge_threshold_w == 0
            ):
                self.sensor_original_mode.set(MODE_PEAK_SHAVING)
            elif (
                self.operation_settings.charge_threshold_w > 0
                and self.operation_settings.discharge_threshold_w > 0
            ):
                self.sensor_original_mode.set(MODE_BUY)
            elif (
                self.operation_settings.charge_threshold_w < 0
                and self.operation_settings.discharge_threshold_w < 0
            ):
                self.sensor_original_mode.set(MODE_SELL)
            else:
                if (
                    self.sensor_solar_ev_charging.state == STATE_ON
                ):  # TODO: And discharge threshold memory >= 0
                    self.sensor_original_mode.set(MODE_PEAK_SHAVING)
                else:
                    self.sensor_original_mode.set(MODE_SELF)

        _LOGGER.debug(
            "self.primary_peak_shaving_target = %s", self.primary_peak_shaving_target_w
        )
        _LOGGER.debug(
            "self.secondary_peak_shaving_target = %s",
            self.secondary_peak_shaving_target_w,
        )

        if self.primary_peak_shaving_target_w == 0:
            if self.operation_settings.discharge_threshold_w > 0:
                self.primary_peak_shaving_target_w = (
                    self.operation_settings.discharge_threshold_w
                )
        elif self.operation_settings.discharge_threshold_w > 0:
            if (
                0.6
                < (
                    self.operation_settings.discharge_threshold_w
                    / self.primary_peak_shaving_target_w
                )
                < 1.4
            ):
                # If the new value is within 40% of the previous value, update the previous value.
                self.primary_peak_shaving_target_w = (
                    self.operation_settings.discharge_threshold_w
                )
            elif (
                self.operation_settings.discharge_threshold_w
                / self.primary_peak_shaving_target_w
            ) >= 1.4:
                # If the new value is more than 40% higher than the previous primary value,
                # update the secondary value.
                self.secondary_peak_shaving_target_w = (
                    self.operation_settings.discharge_threshold_w
                )
            elif (
                self.operation_settings.discharge_threshold_w
                / self.primary_peak_shaving_target_w
            ) <= 0.6:
                # If the new value is more than 40% lower than the previous primaryvalue,
                # update both primary and secondary value.
                self.secondary_peak_shaving_target_w = (
                    self.primary_peak_shaving_target_w
                )
                self.primary_peak_shaving_target_w = (
                    self.operation_settings.discharge_threshold_w
                )

        if (
            self.sensor_peak_shaving_target.state != self.primary_peak_shaving_target_w
            or self.sensor_secondary_peak_shaving_target.state
            != self.secondary_peak_shaving_target_w
        ):
            if (
                self.sensor_peak_shaving_target.state
                != self.primary_peak_shaving_target_w
            ):
                _LOGGER.debug(
                    "Updating primary peak shaving target sensor from %s to %s",
                    self.sensor_peak_shaving_target.state,
                    self.primary_peak_shaving_target_w,
                )
            if (
                self.sensor_secondary_peak_shaving_target.state
                != self.secondary_peak_shaving_target_w
            ):
                _LOGGER.debug(
                    "Updating secondary peak shaving target sensor from %s to %s",
                    self.sensor_secondary_peak_shaving_target.state,
                    self.secondary_peak_shaving_target_w,
                )

            async with ferro_ai_companion_coordinator_lock:
                # Save the updated values to the data store
                data = await self.data_store.async_load()
                if data is None:
                    data = {}
                data[self.config_entry.entry_id] = {
                    "primary_peak_shaving_target_w": self.primary_peak_shaving_target_w,
                    "secondary_peak_shaving_target_w": self.secondary_peak_shaving_target_w,
                }
                await self.data_store.async_save(data)

        self.sensor_peak_shaving_target.set(self.primary_peak_shaving_target_w)
        self.sensor_secondary_peak_shaving_target.set(
            self.secondary_peak_shaving_target_w
        )

        _LOGGER.debug(
            "self.primary_peak_shaving_target = %s", self.primary_peak_shaving_target_w
        )
        _LOGGER.debug(
            "self.secondary_peak_shaving_target = %s",
            self.secondary_peak_shaving_target_w,
        )

    async def switch_ev_connected_update(self, state: bool):
        """Handle the EV Connected switch"""
        self.switch_ev_connected = state
        _LOGGER.debug("switch_ev_connected_update = %s", state)
        await self.generate_event(ENTITY_KEY_EV_CONNECTED_SWITCH, not state, state)

    async def switch_avoid_import_update(self, state: bool):
        """Handle the Avoid Import switch"""
        self.switch_avoid_import = state
        _LOGGER.debug("switch_avoid_import_update = %s", state)
        await self.generate_event(ENTITY_KEY_AVOID_IMPORT_SWITCH, not state, state)

    async def switch_avoid_battery_usage_update(self, state: bool):
        """Handle the Avoid Battery Usage switch"""
        self.switch_avoid_battery_usage = state
        _LOGGER.debug("switch_avoid_battery_usage_update = %s", state)
        await self.generate_event(
            ENTITY_KEY_AVOID_BATTERY_USAGE_SWITCH, not state, state
        )

    async def switch_force_buying_update(self, state: bool):
        """Handle the Force Buying switch"""
        self.switch_force_buying = state
        _LOGGER.debug("switch_force_buying_update = %s", state)
        await self.generate_event(ENTITY_KEY_FORCE_BUYING_SWITCH, not state, state)

    async def switch_force_selling_update(self, state: bool):
        """Handle the Force Selling switch"""
        self.switch_force_selling = state
        _LOGGER.debug("switch_force_selling_update = %s", state)
        await self.generate_event(ENTITY_KEY_FORCE_SELLING_SWITCH, not state, state)

    async def generate_event(
        self,
        entity_id: str = None,
        old_state=None,
        new_state=None,
    ):
        """Handle entity state changes."""

        state_changed_data: EventStateChangedData = {
            "entity_id": entity_id,
            "old_state": old_state,
            "new_state": new_state,
        }
        event = Event[EventStateChangedData](event_type=None, data=state_changed_data)
        await self.handle_events(event)

    @callback
    async def handle_events(self, event: Event[EventStateChangedData]):
        """Handle state change events.
        EventStateChangedData is supported from Home Assistant 2024.5.5"""

        _LOGGER.debug("FerroAICompanionCoordinator.handle_state_change()")

        # Allowed from HA 2024.4
        entity_id = event.data["entity_id"]
        old_state = event.data["old_state"]
        new_state = event.data["new_state"]

        _LOGGER.debug("entity_id = %s", entity_id)
        _LOGGER.debug("old_state = %s", old_state)
        _LOGGER.debug("new_state = %s", new_state)

        if get_parameter(self.config_entry, CONF_SOLAR_EV_CHARGING_ENABLED, False):

            if self.ev_soc_entity_id and (entity_id == self.ev_soc_entity_id):
                ev_soc_state = self.hass.states.get(self.ev_soc_entity_id)
                if Validator.is_soc_state(ev_soc_state):
                    self.ev_soc_valid = True
                    self.ev_soc = float(ev_soc_state.state)
                else:
                    if self.ev_soc_valid:
                        # Make only one error message per outage.
                        _LOGGER.error("SOC sensor not valid: %s", ev_soc_state)
                    self.ev_soc_valid = False

            if self.ev_target_soc_entity_id and (
                entity_id == self.ev_target_soc_entity_id
            ):
                ev_target_soc_state = self.hass.states.get(self.ev_target_soc_entity_id)
                if Validator.is_soc_state(ev_target_soc_state):
                    self.ev_target_soc_valid = True
                    self.ev_target_soc = float(ev_target_soc_state.state)
                else:
                    if self.ev_target_soc_valid:
                        # Make only one error message per outage.
                        _LOGGER.error(
                            "Target SOC sensor not valid: %s", ev_target_soc_state
                        )
                    self.ev_target_soc_valid = False

            if self.solar_forecast_today_remaining_entity_id and (
                entity_id == self.solar_forecast_today_remaining_entity_id
            ):
                try:
                    remaining_solar_energy_wh = (
                        float(
                            self.hass.states.get(
                                self.solar_forecast_today_remaining_entity_id
                            ).state
                        )
                        * 1000
                    )  # Convert kWh to Wh
                    self.solar_ev_charging.set_start_stop_soc(
                        remaining_solar_energy_wh,
                        self.assumed_house_consumption,
                        self.operation_settings.max_soc,
                    )

                except (ValueError, TypeError) as e:
                    _LOGGER.error("Failed to fetch remaining solar energy: %s", e)

        # Handle override switches
        if entity_id in [
            ENTITY_KEY_AVOID_IMPORT_SWITCH,
            ENTITY_KEY_AVOID_BATTERY_USAGE_SWITCH,
            ENTITY_KEY_FORCE_BUYING_SWITCH,
            ENTITY_KEY_FORCE_SELLING_SWITCH,
        ]:
            if new_state is True:
                await self.operation_settings.override(
                    entity_id, self.primary_peak_shaving_target_w
                )
            else:
                if (
                    self.switch_avoid_battery_usage is False
                    and self.switch_avoid_import is False
                    and self.switch_force_buying is False
                    and self.switch_force_selling is False
                ):
                    # If all override switches are off, reset the operation settings
                    await self.operation_settings.stop_override()

        # Handle triggers
        # TODO: Add TRIGGERS

    async def add_sensor(self, sensors: list[FerroAICompanionSensor]):
        """Set up sensor"""
        for sensor in sensors:
            if isinstance(sensor, FerroAICompanionSensorMode):
                self.sensor_mode = sensor
            if isinstance(sensor, FerroAICompanionSensorOriginalMode):
                self.sensor_original_mode = sensor
            if isinstance(sensor, FerroAICompanionSensorPeakShavingTarget):
                self.sensor_peak_shaving_target = sensor
            if isinstance(sensor, FerroAICompanionSensorSecondaryPeakShavingTarget):
                self.sensor_secondary_peak_shaving_target = sensor
            if isinstance(sensor, FerroAICompanionSensorChargingCurrent):
                self.sensor_charging_current = sensor
            if isinstance(sensor, FerroAICompanionSensorSolarEVCharging):
                self.sensor_solar_ev_charging = sensor

        if get_parameter(self.config_entry, CONF_SOLAR_EV_CHARGING_ENABLED, False):

            # Initialize EV SOC sensor
            self.ev_soc_entity_id = get_parameter(self.config_entry, CONF_EV_SOC_SENSOR)
            ev_soc_state = self.hass.states.get(self.ev_soc_entity_id)
            if Validator.is_soc_state(ev_soc_state):
                await self.generate_event(
                    self.ev_soc_entity_id, None, ev_soc_state.state
                )

            # Initialize EV Target SOC sensor
            self.ev_target_soc_entity_id = get_parameter(
                self.config_entry, CONF_EV_TARGET_SOC_SENSOR
            )
            ev_target_soc_state = self.hass.states.get(self.ev_target_soc_entity_id)
            if Validator.is_soc_state(ev_target_soc_state):
                await self.generate_event(
                    self.ev_target_soc_entity_id, None, ev_target_soc_state.state
                )

            # Initialize Solar Forecast Today Remaining sensor
            self.solar_forecast_today_remaining_entity_id = get_parameter(
                self.config_entry, CONF_SOLAR_FORECAST_TODAY_REMAINING
            )
            solar_forecast_today_remaining_state = self.hass.states.get(
                self.solar_forecast_today_remaining_entity_id
            )
            if Validator.is_float(solar_forecast_today_remaining_state):
                await self.generate_event(
                    self.solar_forecast_today_remaining_entity_id,
                    None,
                    solar_forecast_today_remaining_state.state,
                )

            # Assume Home Assistant 2024.6 or newer
            self.listeners.append(
                async_track_state_change_event(
                    self.hass,
                    [
                        self.solar_forecast_today_remaining_entity_id,
                        self.ev_target_soc_entity_id,
                        self.ev_soc_entity_id,
                    ],
                    self.handle_events,
                )
            )

    def validate_input_sensors(self) -> str:
        """Check that all input sensors returns values."""

        if get_parameter(self.config_entry, CONF_SOLAR_EV_CHARGING_ENABLED, False):

            ev_soc = get_parameter(self.config_entry, CONF_EV_SOC_SENSOR)
            ev_soc_state = self.hass.states.get(ev_soc)
            if ev_soc_state is None or ev_soc_state.state is None:
                return "Input sensors not ready."

            ev_target_soc = get_parameter(self.config_entry, CONF_EV_TARGET_SOC_SENSOR)
            if len(ev_target_soc) > 0:  # Check if the sensor exists
                ev_target_soc_state = self.hass.states.get(ev_target_soc)
                if ev_target_soc_state is None or ev_target_soc_state.state is None:
                    return "Input sensors not ready."

            remaining_energy = get_parameter(
                self.config_entry, CONF_SOLAR_FORECAST_TODAY_REMAINING
            )
            remaining_energy_state = self.hass.states.get(remaining_energy)
            if remaining_energy_state is None or remaining_energy_state.state is None:
                return "Input sensors not ready."

        return None
