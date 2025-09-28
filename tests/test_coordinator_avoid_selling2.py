"""Test ferro_ai_companion coordinator."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.ferro_ai_companion import async_setup_entry
from custom_components.ferro_ai_companion.coordinator import (
    FerroAICompanionCoordinator,
)
from custom_components.ferro_ai_companion.const import (
    BUY_POWER_OFFSET,
    DOMAIN,
    ENTITY_KEY_COMPANION_MODE_SELECT,
    MODE_AUTO,
    MODE_BUY,
    MODE_PEAK_CHARGE,
    MODE_SELF,
    MODE_SELL,
    OVERRIDE_OFFSET,
)

from tests.const import MOCK_CONFIG_USER_TEMP1

# pylint: disable=unused-argument


async def test_coordinator_avoid_selling2(
    hass: HomeAssistant, skip_service_calls, mock_operation_settings_fetch_all_data
):
    """Test Coordinator avoid selling."""

    mock_operation_settings_fetch_all_data(
        max_soc=90,
        discharge_threshold_w=1000,
        charge_threshold_w=500,
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

    # Test scenario
    # - AUTO self
    # - avoid_selling = True
    # - BUY
    # - avoid_selling = False
    # - avoid_selling = True
    # - SELL
    # - AUTO sell
    # - avoid_selling = False
    # - avoid_selling = True
    # - Quarterly update with self values
    # - Quarterly update with sell values

    # MODE_AUTO with self
    coordinator.operation_settings.discharge_threshold_w = 0
    coordinator.operation_settings.charge_threshold_w = 0
    coordinator.operation_settings.original_discharge_threshold_w = coordinator.operation_settings.discharge_threshold_w
    coordinator.operation_settings.original_charge_threshold_w = coordinator.operation_settings.charge_threshold_w
    mock_operation_settings_fetch_all_data(
        discharge_threshold_w=coordinator.operation_settings.discharge_threshold_w,
        charge_threshold_w=coordinator.operation_settings.charge_threshold_w,
        override_active=coordinator.operation_settings.override_active,
    )
    await coordinator.generate_event(ENTITY_KEY_COMPANION_MODE_SELECT, new_state=MODE_AUTO)
    assert coordinator.select_companion_mode == MODE_AUTO
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_SELF

    # Avoid selling = True, threshold should remain changed
    await coordinator.switch_avoid_selling_update(True)
    assert coordinator.operation_settings.discharge_threshold_w == 0
    assert coordinator.operation_settings.charge_threshold_w == 0
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_SELF

    # MODE_BUY
    await coordinator.generate_event(ENTITY_KEY_COMPANION_MODE_SELECT, new_state=MODE_BUY)
    assert coordinator.select_companion_mode == MODE_BUY
    assert coordinator.operation_settings.discharge_threshold_w == 1000 + BUY_POWER_OFFSET + OVERRIDE_OFFSET
    assert coordinator.operation_settings.charge_threshold_w == 1000 + BUY_POWER_OFFSET + OVERRIDE_OFFSET
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_BUY

    # Avoid selling = False, threshold should remain changed
    await coordinator.switch_avoid_selling_update(False)
    assert coordinator.operation_settings.discharge_threshold_w == 1000 + BUY_POWER_OFFSET + OVERRIDE_OFFSET
    assert coordinator.operation_settings.charge_threshold_w == 1000 + BUY_POWER_OFFSET + OVERRIDE_OFFSET
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_BUY

    # Avoid selling = True, threshold should remain changed
    await coordinator.switch_avoid_selling_update(True)
    assert coordinator.operation_settings.discharge_threshold_w == 1000 + BUY_POWER_OFFSET + OVERRIDE_OFFSET
    assert coordinator.operation_settings.charge_threshold_w == 1000 + BUY_POWER_OFFSET + OVERRIDE_OFFSET
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_BUY

    # MODE_SELL
    await coordinator.generate_event(ENTITY_KEY_COMPANION_MODE_SELECT, new_state=MODE_SELL)
    assert coordinator.select_companion_mode == MODE_SELL
    assert coordinator.operation_settings.discharge_threshold_w == -100000 + OVERRIDE_OFFSET
    assert coordinator.operation_settings.charge_threshold_w == -100000 + OVERRIDE_OFFSET
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_SELL

    # MODE_AUTO with sell
    coordinator.operation_settings.discharge_threshold_w = -100000
    coordinator.operation_settings.charge_threshold_w = -100000
    coordinator.operation_settings.original_discharge_threshold_w = coordinator.operation_settings.discharge_threshold_w
    coordinator.operation_settings.original_charge_threshold_w = coordinator.operation_settings.charge_threshold_w
    mock_operation_settings_fetch_all_data(
        discharge_threshold_w=coordinator.operation_settings.discharge_threshold_w,
        charge_threshold_w=coordinator.operation_settings.charge_threshold_w,
        override_active=coordinator.operation_settings.override_active,
    )
    await coordinator.generate_event(ENTITY_KEY_COMPANION_MODE_SELECT, new_state=MODE_AUTO)
    assert coordinator.select_companion_mode == MODE_AUTO
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_PEAK_CHARGE

    # Avoid selling = False, threshold should be restored to sell
    await coordinator.switch_avoid_selling_update(False)
    assert coordinator.operation_settings.discharge_threshold_w == -100000
    assert coordinator.operation_settings.charge_threshold_w == -100000
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_SELL

    # Avoid selling = True, threshold should change
    await coordinator.switch_avoid_selling_update(True)
    assert coordinator.operation_settings.discharge_threshold_w == 1000 + OVERRIDE_OFFSET
    assert coordinator.operation_settings.charge_threshold_w == 0 + OVERRIDE_OFFSET
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_PEAK_CHARGE
    assert coordinator.operation_settings.override_active

    # Quarterly update with self values
    mock_operation_settings_fetch_all_data(
        discharge_threshold_w=0,
        charge_threshold_w=0,
        override_active=coordinator.operation_settings.override_active,
    )
    await coordinator.update_quarterly()
    assert coordinator.operation_settings.discharge_threshold_w == 0
    assert coordinator.operation_settings.charge_threshold_w == 0
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_SELF
    assert coordinator.operation_settings.override_active is False

    # Quarterly update with sell values
    mock_operation_settings_fetch_all_data(
        discharge_threshold_w=-100000,
        charge_threshold_w=-100000,
        override_active=coordinator.operation_settings.override_active,
    )
    await coordinator.update_quarterly()
    assert coordinator.operation_settings.discharge_threshold_w == 1000 + OVERRIDE_OFFSET
    assert coordinator.operation_settings.charge_threshold_w == 0 + OVERRIDE_OFFSET
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_PEAK_CHARGE
    assert coordinator.operation_settings.override_active is True

    # Unsubscribe to listeners
    coordinator.unsubscribe_listeners()
