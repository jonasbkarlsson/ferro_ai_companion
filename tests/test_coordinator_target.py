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
    CAPACITY_TARIFF_DIFFERENT_DAY_NIGHT,
    DOMAIN,
    ENTITY_KEY_COMPANION_MODE_SELECT,
    MODE_AUTO,
    MODE_BUY,
    MODE_PEAK_CHARGE,
    MODE_SELF,
    OVERRIDE_OFFSET,
)

from tests.const import MOCK_CONFIG_USER_TEMP1

# pylint: disable=unused-argument


async def test_coordinator_target(
    hass: HomeAssistant,
    skip_service_calls,
    set_cet_timezone,
    freezer,
    mock_operation_settings_fetch_all_data,
):
    """Test Coordinator avoid selling."""

    mock_operation_settings_fetch_all_data(
        max_soc=90,
        discharge_threshold_w=1000,
        charge_threshold_w=500,
    )

    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_USER_TEMP1, entry_id="test"
    )
    config_entry.mock_state(hass=hass, state=ConfigEntryState.LOADED)
    config_entry.add_to_hass(hass)
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], FerroAICompanionCoordinator
    )
    coordinator: FerroAICompanionCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Set initial targets
    freezer.move_to("2025-10-04T00:10:00+02:00")
    coordinator.primary_peak_shaving_target_w = 2732
    coordinator.secondary_peak_shaving_target_w = 5465
    coordinator.select_companion_mode = MODE_AUTO
    coordinator.operation_settings.override_active = False
    coordinator.operation_settings.discharge_threshold_w = 0
    coordinator.operation_settings.charge_threshold_w = 0
    coordinator.operation_settings.original_discharge_threshold_w = (
        coordinator.operation_settings.discharge_threshold_w
    )
    coordinator.operation_settings.original_charge_threshold_w = (
        coordinator.operation_settings.charge_threshold_w
    )
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_SELF
    mode = await coordinator.operation_settings.get_original_mode()
    assert mode == MODE_SELF
    assert coordinator.operation_settings.override_active is False
    assert coordinator.primary_peak_shaving_target_w == 2732
    assert coordinator.secondary_peak_shaving_target_w == 5465
    assert coordinator.capacity_tariff == CAPACITY_TARIFF_DIFFERENT_DAY_NIGHT

    # Quarterly update with sell values
    mock_operation_settings_fetch_all_data(
        discharge_threshold_w=0,
        charge_threshold_w=0,
        override_active=coordinator.operation_settings.override_active,
    )
    await coordinator.update_quarterly()
    assert coordinator.primary_peak_shaving_target_w == 2732
    assert coordinator.secondary_peak_shaving_target_w == 5465
    assert coordinator.operation_settings.discharge_threshold_w == 0
    assert coordinator.operation_settings.charge_threshold_w == 0
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_SELF
    assert coordinator.operation_settings.override_active is False
    mode = await coordinator.operation_settings.get_original_mode()
    assert mode == MODE_SELF

    # Quarterly update with sell values
    mock_operation_settings_fetch_all_data(
        discharge_threshold_w=6011,
        charge_threshold_w=0,
        override_active=coordinator.operation_settings.override_active,
    )
    await coordinator.update_quarterly()
    assert coordinator.primary_peak_shaving_target_w == 2732
    assert coordinator.secondary_peak_shaving_target_w == 6011
    assert coordinator.operation_settings.discharge_threshold_w == 6011
    assert coordinator.operation_settings.charge_threshold_w == 0
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_PEAK_CHARGE
    assert coordinator.operation_settings.override_active is False
    mode = await coordinator.operation_settings.get_original_mode()
    assert mode == MODE_PEAK_CHARGE

    # Overide to BUY
    await coordinator.generate_event(
        ENTITY_KEY_COMPANION_MODE_SELECT, new_state=MODE_BUY
    )
    assert coordinator.select_companion_mode == MODE_BUY
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_BUY
    mode = await coordinator.operation_settings.get_original_mode()
    assert mode == MODE_PEAK_CHARGE
    assert coordinator.operation_settings.override_active is True
    assert coordinator.primary_peak_shaving_target_w == 2732
    assert coordinator.secondary_peak_shaving_target_w == 6011
    assert (
        coordinator.operation_settings.discharge_threshold_w
        == 6011 + BUY_POWER_OFFSET + OVERRIDE_OFFSET
    )  # 5265, should be 5812
    assert (
        coordinator.operation_settings.charge_threshold_w
        == 6011 + BUY_POWER_OFFSET + OVERRIDE_OFFSET
    )  # 5265

    # Quarterly update, first after 06:00
    freezer.move_to("2025-10-04T06:05:00+02:00")
    mock_operation_settings_fetch_all_data(
        discharge_threshold_w=3005,
        charge_threshold_w=0,
        override_active=coordinator.operation_settings.override_active,
    )
    await coordinator.update_quarterly()
    assert coordinator.primary_peak_shaving_target_w == 3005
    assert coordinator.secondary_peak_shaving_target_w == 6011
    assert (
        coordinator.operation_settings.discharge_threshold_w
        == 3005 + BUY_POWER_OFFSET + OVERRIDE_OFFSET
    )  # 2533
    assert (
        coordinator.operation_settings.charge_threshold_w
        == 3005 + BUY_POWER_OFFSET + OVERRIDE_OFFSET
    )  # 2533
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_BUY
    mode = await coordinator.operation_settings.get_original_mode()
    assert mode == MODE_PEAK_CHARGE
    assert coordinator.operation_settings.override_active is True

    # Quarterly update, FerroAI changed the values
    freezer.move_to("2025-10-04T06:20:00+02:00")
    mock_operation_settings_fetch_all_data(
        discharge_threshold_w=3005,
        charge_threshold_w=0,
        override_active=coordinator.operation_settings.override_active,
    )
    await coordinator.update_quarterly()
    assert coordinator.primary_peak_shaving_target_w == 3005
    assert coordinator.secondary_peak_shaving_target_w == 6011
    assert (
        coordinator.operation_settings.discharge_threshold_w
        == 3005 + BUY_POWER_OFFSET + OVERRIDE_OFFSET
    )
    assert (
        coordinator.operation_settings.charge_threshold_w
        == 3005 + BUY_POWER_OFFSET + OVERRIDE_OFFSET
    )
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_BUY
    mode = await coordinator.operation_settings.get_original_mode()
    assert mode == MODE_PEAK_CHARGE
    assert coordinator.operation_settings.override_active is True

    # Quarterly update, FerroAI did not changed the values
    freezer.move_to("2025-10-04T06:20:00+02:00")
    mock_operation_settings_fetch_all_data(
        discharge_threshold_w=2806,
        charge_threshold_w=2806,
        override_active=coordinator.operation_settings.override_active,
    )
    await coordinator.update_quarterly()
    assert coordinator.primary_peak_shaving_target_w == 3005
    assert coordinator.secondary_peak_shaving_target_w == 6011
    assert (
        coordinator.operation_settings.discharge_threshold_w
        == 3005 + BUY_POWER_OFFSET + OVERRIDE_OFFSET
    )
    assert (
        coordinator.operation_settings.charge_threshold_w
        == 3005 + BUY_POWER_OFFSET + OVERRIDE_OFFSET
    )
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_BUY
    mode = await coordinator.operation_settings.get_original_mode()
    assert mode == MODE_PEAK_CHARGE
    assert coordinator.operation_settings.override_active is True

    # Unsubscribe to listeners
    coordinator.unsubscribe_listeners()
