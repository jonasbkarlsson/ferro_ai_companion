"""Test ferro_ai_companion coordinator."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.ferro_ai_companion import async_setup_entry
from custom_components.ferro_ai_companion.coordinator import (
    FerroAICompanionCoordinator,
)
from custom_components.ferro_ai_companion.const import (
    DOMAIN,
    MODE_AUTO,
    MODE_PEAK_CHARGE,
    MODE_PEAK_SELL,
    MODE_SELF,
    MODE_SELL,
    OVERRIDE_OFFSET,
)

from tests.const import MOCK_CONFIG_USER_TEMP1

# pylint: disable=unused-argument


async def test_coordinator_avoid_selling(
    hass: HomeAssistant, skip_service_calls, mock_operation_settings_fetch_all_data
):
    """Test Coordinator avoid selling."""

    mock_operation_settings_fetch_all_data(
        max_soc=90,
        discharge_threshold_w=1000,
        charge_threshold_w=500,
        original_discharge_threshold_w=1000,
        original_charge_threshold_w=500,
    )

    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG_USER_TEMP1, entry_id="test")
    config_entry.mock_state(hass=hass, state=ConfigEntryState.LOADED)
    config_entry.add_to_hass(hass)
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], FerroAICompanionCoordinator
    )
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Set initial targets
    coordinator.primary_peak_shaving_target_w = 1000
    coordinator.secondary_peak_shaving_target_w = 2000

    coordinator.operation_settings.original_discharge_threshold_w = 1000
    coordinator.update_peak_shaving_targets()
    assert coordinator.primary_peak_shaving_target_w == 1000
    assert coordinator.secondary_peak_shaving_target_w == 2000

    # Test MODE_SELL
    coordinator.select_companion_mode = MODE_SELL
    coordinator.operation_settings.discharge_threshold_w = -100000
    coordinator.operation_settings.charge_threshold_w = -100000
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_SELL
    await coordinator.switch_avoid_selling_update(False)
    # Threshold should remain unchanged
    assert coordinator.operation_settings.discharge_threshold_w == -100000
    assert coordinator.operation_settings.charge_threshold_w == -100000
    await coordinator.switch_avoid_selling_update(True)
    # Threshold should remain unchanged
    assert coordinator.operation_settings.discharge_threshold_w == -100000
    assert coordinator.operation_settings.charge_threshold_w == -100000

    # Test MODE_PEAK_SELL
    coordinator.select_companion_mode = MODE_PEAK_SELL
    coordinator.operation_settings.discharge_threshold_w = 1000
    coordinator.operation_settings.charge_threshold_w = -100000
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_PEAK_SELL
    await coordinator.switch_avoid_selling_update(False)
    # Threshold should remain unchanged
    assert coordinator.operation_settings.discharge_threshold_w == 1000
    assert coordinator.operation_settings.charge_threshold_w == -100000
    await coordinator.switch_avoid_selling_update(True)
    # Threshold should remain unchanged
    assert coordinator.operation_settings.discharge_threshold_w == 1000
    assert coordinator.operation_settings.charge_threshold_w == -100000

    # Test MODE_PEAK_CHARGE
    coordinator.select_companion_mode = MODE_PEAK_CHARGE
    coordinator.operation_settings.discharge_threshold_w = 1000
    coordinator.operation_settings.charge_threshold_w = 0
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_PEAK_CHARGE
    await coordinator.switch_avoid_selling_update(False)
    # Threshold should remain unchanged
    assert coordinator.operation_settings.discharge_threshold_w == 1000
    assert coordinator.operation_settings.charge_threshold_w == 0
    await coordinator.switch_avoid_selling_update(True)
    # Threshold should remain unchanged
    assert coordinator.operation_settings.discharge_threshold_w == 1000
    assert coordinator.operation_settings.charge_threshold_w == 0

    # Test MODE_SELF
    coordinator.select_companion_mode = MODE_SELF
    coordinator.operation_settings.discharge_threshold_w = 0
    coordinator.operation_settings.charge_threshold_w = 0
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_SELF
    await coordinator.switch_avoid_selling_update(False)
    # Threshold should remain unchanged
    assert coordinator.operation_settings.discharge_threshold_w == 0
    assert coordinator.operation_settings.charge_threshold_w == 0
    await coordinator.switch_avoid_selling_update(True)
    # Threshold should remain unchanged
    assert coordinator.operation_settings.discharge_threshold_w == 0
    assert coordinator.operation_settings.charge_threshold_w == 0

    # Test MODE_AUTO with selling
    coordinator.select_companion_mode = MODE_AUTO
    coordinator.operation_settings.discharge_threshold_w = -100000
    coordinator.operation_settings.charge_threshold_w = -100000
    coordinator.operation_settings.original_discharge_threshold_w = coordinator.operation_settings.discharge_threshold_w
    coordinator.operation_settings.original_charge_threshold_w = coordinator.operation_settings.charge_threshold_w
    mock_operation_settings_fetch_all_data(
        discharge_threshold_w=coordinator.operation_settings.discharge_threshold_w,
        charge_threshold_w=coordinator.operation_settings.charge_threshold_w,
        original_discharge_threshold_w=coordinator.operation_settings.original_discharge_threshold_w ,
        original_charge_threshold_w=coordinator.operation_settings.original_charge_threshold_w,
    )
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_SELL
    # Threshold should be changed
    await coordinator.switch_avoid_selling_update(True)
    assert coordinator.operation_settings.discharge_threshold_w == 1000 + OVERRIDE_OFFSET
    assert coordinator.operation_settings.charge_threshold_w == 0 + OVERRIDE_OFFSET
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_PEAK_CHARGE
    # Threshold should be restored
    await coordinator.switch_avoid_selling_update(False)
    assert coordinator.operation_settings.discharge_threshold_w == -100000
    assert coordinator.operation_settings.charge_threshold_w == -100000

    # Test MODE_AUTO with peak_selling
    coordinator.select_companion_mode = MODE_AUTO
    coordinator.operation_settings.discharge_threshold_w = 1000
    coordinator.operation_settings.charge_threshold_w = -100000
    coordinator.operation_settings.original_discharge_threshold_w = coordinator.operation_settings.discharge_threshold_w
    coordinator.operation_settings.original_charge_threshold_w = coordinator.operation_settings.charge_threshold_w
    mock_operation_settings_fetch_all_data(
        discharge_threshold_w=coordinator.operation_settings.discharge_threshold_w,
        charge_threshold_w=coordinator.operation_settings.charge_threshold_w,
        original_discharge_threshold_w=coordinator.operation_settings.original_discharge_threshold_w ,
        original_charge_threshold_w=coordinator.operation_settings.original_charge_threshold_w,
    )
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_PEAK_SELL
    # Threshold should be changed
    await coordinator.switch_avoid_selling_update(True)
    assert coordinator.operation_settings.discharge_threshold_w == 1000 + OVERRIDE_OFFSET
    assert coordinator.operation_settings.charge_threshold_w == 0 + OVERRIDE_OFFSET
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_PEAK_CHARGE
    # Threshold should be restored
    await coordinator.switch_avoid_selling_update(False)
    assert coordinator.operation_settings.discharge_threshold_w == 1000
    assert coordinator.operation_settings.charge_threshold_w == -100000

    # Test MODE_AUTO with self
    coordinator.select_companion_mode = MODE_AUTO
    coordinator.operation_settings.discharge_threshold_w = 0
    coordinator.operation_settings.charge_threshold_w = 0
    coordinator.operation_settings.original_discharge_threshold_w = coordinator.operation_settings.discharge_threshold_w
    coordinator.operation_settings.original_charge_threshold_w = coordinator.operation_settings.charge_threshold_w
    mock_operation_settings_fetch_all_data(
        discharge_threshold_w=coordinator.operation_settings.discharge_threshold_w,
        charge_threshold_w=coordinator.operation_settings.charge_threshold_w,
        original_discharge_threshold_w=coordinator.operation_settings.original_discharge_threshold_w ,
        original_charge_threshold_w=coordinator.operation_settings.original_charge_threshold_w,
    )
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_SELF
    # Threshold should remain changed
    await coordinator.switch_avoid_selling_update(True)
    assert coordinator.operation_settings.discharge_threshold_w == 0
    assert coordinator.operation_settings.charge_threshold_w == 0
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_SELF
    # Threshold should be restored
    await coordinator.switch_avoid_selling_update(False)
    assert coordinator.operation_settings.discharge_threshold_w == 0
    assert coordinator.operation_settings.charge_threshold_w == 0

    # Unsubscribe to listeners
    coordinator.unsubscribe_listeners()
