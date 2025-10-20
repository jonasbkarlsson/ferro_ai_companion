"""Test ferro_ai_companion number."""

from unittest.mock import patch
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import MAJOR_VERSION, MINOR_VERSION
from homeassistant.core import HomeAssistant
from homeassistant.components.number import NumberExtraStoredData

from custom_components.ferro_ai_companion import (
    async_setup_entry,
    async_unload_entry,
)
from custom_components.ferro_ai_companion.const import (
    DOMAIN,
    NUMBER,
)
from custom_components.ferro_ai_companion.coordinator import (
    FerroAICompanionCoordinator,
)
from custom_components.ferro_ai_companion.number import (
    FerroAICompanionNumberAssumedHouseConsumption,
    FerroAICompanionNumberMaxChargingCurrent,
    FerroAICompanionNumberMinChargingCurrent,
)

from .const import MOCK_CONFIG_ALL

# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.


# pylint: disable=unused-argument
async def test_number(
    hass,
    bypass_validate_input,
    mock_operation_settings_fetch_all_data,
    skip_service_calls,
):
    """Test sensor properties."""
    mock_operation_settings_fetch_all_data(
        max_soc=90,
        discharge_threshold_w=6011,
        charge_threshold_w=0,
    )

    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_ALL,
        entry_id="test",
        title="ferro_ai_companion",
        state=ConfigEntryState.LOADED,
    )
    config_entry.add_to_hass(hass)

    # Set up the entry and assert that the values set during setup are where we expect
    # them to be.
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], FerroAICompanionCoordinator
    )
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Get the numbers
    number_max_charging_current: FerroAICompanionNumberMaxChargingCurrent = hass.data[
        "entity_components"
    ][NUMBER].get_entity("number.ferro_ai_companion_max_charging_current")
    number_min_charging_current: FerroAICompanionNumberMinChargingCurrent = hass.data[
        "entity_components"
    ][NUMBER].get_entity("number.ferro_ai_companion_min_charging_current")
    number_assumed_house_consumption: FerroAICompanionNumberAssumedHouseConsumption = (
        hass.data["entity_components"][NUMBER].get_entity(
            "number.ferro_ai_companion_assumed_house_consumption"
        )
    )
    assert number_max_charging_current
    assert number_min_charging_current
    assert number_assumed_house_consumption
    assert isinstance(
        number_max_charging_current, FerroAICompanionNumberMaxChargingCurrent
    )
    assert isinstance(
        number_min_charging_current, FerroAICompanionNumberMinChargingCurrent
    )
    assert isinstance(
        number_assumed_house_consumption, FerroAICompanionNumberAssumedHouseConsumption
    )

    # Test the numbers

    assert number_max_charging_current.native_value == 16.0
    assert number_min_charging_current.native_value == 6.0
    assert number_assumed_house_consumption.native_value == 0

    await number_max_charging_current.async_set_native_value(8.0)
    assert coordinator.max_charging_current == 8.0

    await number_min_charging_current.async_set_native_value(7.0)
    assert coordinator.min_charging_current == 7.0

    await number_assumed_house_consumption.async_set_native_value(2000)
    assert coordinator.assumed_house_consumption == 2000

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]


@pytest.fixture(name="mock_last_state_number")
def mock_last_state_number_fixture():
    """Mock last state."""

    restored: NumberExtraStoredData = NumberExtraStoredData.from_dict(
        {
            "native_max_value": 32.0,
            "native_min_value": 1.0,
            "native_step": 1.0,
            "native_unit_of_measurement": "A",
            "native_value": 12.0,
        }
    )
    with patch(
        "homeassistant.components.number.RestoreNumber.async_get_last_number_data",
        return_value=restored,
    ):
        yield


async def test_number_restore(
    hass: HomeAssistant,
    bypass_validate_input,
    mock_last_state_number,
    mock_operation_settings_fetch_all_data,
    skip_service_calls,
):
    """Test sensor properties."""
    mock_operation_settings_fetch_all_data(
        max_soc=90,
        discharge_threshold_w=6011,
        charge_threshold_w=0,
    )

    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_ALL, entry_id="test", title="ferro_ai_companion"
    )
    if MAJOR_VERSION > 2024 or (MAJOR_VERSION == 2024 and MINOR_VERSION >= 7):
        config_entry.mock_state(hass=hass, state=ConfigEntryState.LOADED)
    config_entry.add_to_hass(hass)
    await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    number_max_charging_current: FerroAICompanionNumberMaxChargingCurrent = hass.data[
        "entity_components"
    ][NUMBER].get_entity("number.ferro_ai_companion_max_charging_current")

    await number_max_charging_current.async_set_native_value(10.0)
    assert number_max_charging_current.native_value == 10.0

    await number_max_charging_current.async_added_to_hass()
    assert number_max_charging_current.native_value == 12.0

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    await hass.async_block_till_done()
    assert config_entry.entry_id not in hass.data[DOMAIN]
