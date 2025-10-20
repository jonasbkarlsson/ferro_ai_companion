"""Test ferro_ai_companion coordinator."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.ferro_ai_companion import async_setup_entry
from custom_components.ferro_ai_companion.coordinator import (
    FerroAICompanionCoordinator,
)
from custom_components.ferro_ai_companion.const import DOMAIN

from tests.const import MOCK_CONFIG_ALL


# pylint: disable=unused-argument
async def test_coordinator(
    hass: HomeAssistant,
    skip_service_calls,
    set_cet_timezone,
    bypass_validate_input,
    mock_operation_settings_fetch_all_data,
):
    """Test Coordinator."""

    mock_operation_settings_fetch_all_data(
        max_soc=90,
        discharge_threshold_w=6011,
        charge_threshold_w=0,
    )

    #    entity_registry: EntityRegistry = async_entity_registry_get(hass)

    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG_ALL, entry_id="test")
    config_entry.mock_state(hass=hass, state=ConfigEntryState.LOADED)
    config_entry.add_to_hass(hass)
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], FerroAICompanionCoordinator
    )
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    assert coordinator is not None

    # Unsubscribe to listeners
    coordinator.unsubscribe_listeners()


async def test_coordinator_update_targets1(
    hass: HomeAssistant, skip_service_calls, set_cet_timezone, bypass_validate_input
):
    """Test Coordinator."""

    #    entity_registry: EntityRegistry = async_entity_registry_get(hass)

    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG_ALL, entry_id="test")
    config_entry.mock_state(hass=hass, state=ConfigEntryState.LOADED)
    config_entry.add_to_hass(hass)
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], FerroAICompanionCoordinator
    )
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    assert coordinator is not None

    # Set initial targets
    coordinator.primary_peak_shaving_target_w = 1000
    coordinator.secondary_peak_shaving_target_w = 2000

    coordinator.operation_settings.original_discharge_threshold_w = 1000
    coordinator.update_peak_shaving_targets()
    assert coordinator.primary_peak_shaving_target_w == 1000
    assert coordinator.secondary_peak_shaving_target_w == 2000

    coordinator.operation_settings.original_discharge_threshold_w = 2000
    coordinator.update_peak_shaving_targets()
    assert coordinator.primary_peak_shaving_target_w == 1000
    assert coordinator.secondary_peak_shaving_target_w == 2000

    coordinator.operation_settings.original_discharge_threshold_w = 900
    coordinator.update_peak_shaving_targets()
    assert coordinator.primary_peak_shaving_target_w == 900
    assert coordinator.secondary_peak_shaving_target_w == 2000

    coordinator.operation_settings.original_discharge_threshold_w = 1100
    coordinator.update_peak_shaving_targets()
    assert coordinator.primary_peak_shaving_target_w == 1100
    assert coordinator.secondary_peak_shaving_target_w == 2000

    coordinator.operation_settings.original_discharge_threshold_w = 2100
    coordinator.update_peak_shaving_targets()
    assert coordinator.primary_peak_shaving_target_w == 1100
    assert coordinator.secondary_peak_shaving_target_w == 2100

    coordinator.operation_settings.original_discharge_threshold_w = 1900
    coordinator.update_peak_shaving_targets()
    assert coordinator.primary_peak_shaving_target_w == 1100
    assert coordinator.secondary_peak_shaving_target_w == 1900

    # Unsubscribe to listeners
    coordinator.unsubscribe_listeners()


async def test_coordinator_update_targets2(
    hass: HomeAssistant, skip_service_calls, set_cet_timezone, bypass_validate_input
):
    """Test Coordinator."""

    #    entity_registry: EntityRegistry = async_entity_registry_get(hass)

    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG_ALL, entry_id="test")
    config_entry.mock_state(hass=hass, state=ConfigEntryState.LOADED)
    config_entry.add_to_hass(hass)
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], FerroAICompanionCoordinator
    )
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    assert coordinator is not None

    # Set initial targets
    coordinator.primary_peak_shaving_target_w = 1086
    coordinator.secondary_peak_shaving_target_w = 2172

    coordinator.operation_settings.original_discharge_threshold_w = 1086
    coordinator.update_peak_shaving_targets()
    assert coordinator.primary_peak_shaving_target_w == 1086
    assert coordinator.secondary_peak_shaving_target_w == 2172

    coordinator.operation_settings.original_discharge_threshold_w = 710
    coordinator.update_peak_shaving_targets()
    assert coordinator.primary_peak_shaving_target_w == 710
    assert coordinator.secondary_peak_shaving_target_w == 2172

    coordinator.operation_settings.original_discharge_threshold_w = 1087
    coordinator.update_peak_shaving_targets()
    assert coordinator.primary_peak_shaving_target_w == 1087
    assert coordinator.secondary_peak_shaving_target_w == 2172

    coordinator.operation_settings.original_discharge_threshold_w = 2682
    coordinator.update_peak_shaving_targets()
    assert coordinator.primary_peak_shaving_target_w == 1087
    assert coordinator.secondary_peak_shaving_target_w == 2682

    coordinator.operation_settings.original_discharge_threshold_w = 1341
    coordinator.update_peak_shaving_targets()
    assert coordinator.primary_peak_shaving_target_w == 1341
    assert coordinator.secondary_peak_shaving_target_w == 2682

    # Unsubscribe to listeners
    coordinator.unsubscribe_listeners()


async def test_coordinator_update_targets3(
    hass: HomeAssistant, skip_service_calls, set_cet_timezone, bypass_validate_input
):
    """Test Coordinator."""

    #    entity_registry: EntityRegistry = async_entity_registry_get(hass)

    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG_ALL, entry_id="test")
    config_entry.mock_state(hass=hass, state=ConfigEntryState.LOADED)
    config_entry.add_to_hass(hass)
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], FerroAICompanionCoordinator
    )
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    assert coordinator is not None

    # Set initial targets
    coordinator.primary_peak_shaving_target_w = 710
    coordinator.secondary_peak_shaving_target_w = 1341

    coordinator.operation_settings.original_discharge_threshold_w = 2682
    coordinator.update_peak_shaving_targets()
    assert coordinator.primary_peak_shaving_target_w == 710
    assert coordinator.secondary_peak_shaving_target_w == 2682

    coordinator.operation_settings.original_discharge_threshold_w = 1341
    coordinator.update_peak_shaving_targets()
    assert coordinator.primary_peak_shaving_target_w == 1341
    assert coordinator.secondary_peak_shaving_target_w == 2682

    # Unsubscribe to listeners
    coordinator.unsubscribe_listeners()
