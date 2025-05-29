"""Test ferro_ai_companion setup process."""

from homeassistant.const import MAJOR_VERSION, MINOR_VERSION
from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import ConfigEntryNotReady
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ferro_ai_companion import (
    async_migrate_entry,
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.ferro_ai_companion.const import DOMAIN
from custom_components.ferro_ai_companion.coordinator import (
    FerroAICompanionCoordinator,
)

from .const import (
    MOCK_CONFIG_ALL,
    MOCK_CONFIG_ALL_V1,
)


# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.


# pylint: disable=unused-argument
# async def test_setup_unload_and_reload_entry(hass, bypass_get_data):
async def test_setup_unload_and_reload_entry(hass, bypass_validate_input):
    """Test entry setup and unload."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_ALL,
        entry_id="test",
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

    # Reload the entry and assert that the data from above is still there
    assert await async_reload_entry(hass, config_entry) is None
    await hass.async_block_till_done()
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], FerroAICompanionCoordinator
    )

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    await hass.async_block_till_done()
    assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_setup_entry_exception(hass):
    """Test ConfigEntryNotReady when validate_input_sensors returns an error message."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_ALL,
        entry_id="test",
        state=ConfigEntryState.LOADED,
    )
    config_entry.add_to_hass(hass)

    # In this case we are testing the condition where async_setup_entry raises
    # ConfigEntryNotReady using the `error_on_get_data` fixture which simulates
    # an error.
    with pytest.raises(ConfigEntryNotReady):
        assert await async_setup_entry(hass, config_entry)


async def test_setup_with_migration_v1(hass, bypass_validate_input):
    """Test entry migration."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_ALL_V1,
        entry_id="test",
        version=1,
        state=ConfigEntryState.LOADED,
    )
    config_entry.add_to_hass(hass)

    # Migrate from version 1
    assert await async_migrate_entry(hass, config_entry)
    #    Add more here when there are newer versions than 1
    #    assert config_entry.data["TBD"] == TBD

    # Set up the entry and assert that the values set during setup are where we expect
    # them to be.
    assert await async_setup_entry(hass, config_entry)
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], FerroAICompanionCoordinator
    )

    # Reload the entry and assert that the data from above is still there
    # As of v0.13.104 for pytest-homeassistant-custom-component, there seems to be a problem
    # with recreating Mocks for sensor, switch, button, number and select
    # Don't run the following lines for the time being
    # assert await async_reload_entry(hass, config_entry) is None
    # await hass.async_block_till_done()
    # assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    # assert isinstance(
    #     hass.data[DOMAIN][config_entry.entry_id], FerroAICompanionCoordinator
    # )

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_setup_with_migration_from_future(hass, bypass_validate_input):
    """Test entry migration."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_ALL_V1, entry_id="test", version=9999
    )
    config_entry.add_to_hass(hass)

    # Migrate from version 9999
    assert not await async_migrate_entry(hass, config_entry)


async def test_setup_new_integration_name(hass, bypass_validate_input):
    """Test entry setup with new integration name."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_ALL,
        entry_id="test",
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

    # Change title
    hass.config_entries.async_update_entry(config_entry, title="New title")

    # Reload the entry and assert that the data from above is still there
    assert await async_reload_entry(hass, config_entry) is None
    await hass.async_block_till_done()
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], FerroAICompanionCoordinator
    )

    test = hass.data["device_registry"].devices
    device = hass.data["device_registry"].devices[next(iter(test))]
    # The behvior of HA 2024.6 and older (name_by_user is updated)
    # and HA 2024.7 and newer (name is updated) is different.
    assert device.name_by_user == "New title" or device.name == "New title"

    # Change a changed title
    hass.config_entries.async_update_entry(config_entry, title="New title2")

    # Reload the entry and assert that the data from above is still there
    assert await async_reload_entry(hass, config_entry) is None
    await hass.async_block_till_done()
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], FerroAICompanionCoordinator
    )

    test = hass.data["device_registry"].devices
    device = hass.data["device_registry"].devices[next(iter(test))]
    # The behvior of HA 2024.6 and older (name_by_user is updated)
    # and HA 2024.7 and newer (name is updated) is different.
    assert device.name_by_user == "New title2" or device.name == "New title2"

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    await hass.async_block_till_done()
    assert config_entry.entry_id not in hass.data[DOMAIN]
