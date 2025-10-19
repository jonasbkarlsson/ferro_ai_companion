"""Test ferro_ai_companion coordinator."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.ferro_ai_companion import async_setup_entry
from custom_components.ferro_ai_companion.coordinator import (
    FerroAICompanionCoordinator,
)
from custom_components.ferro_ai_companion.const import (
    CAPACITY_TARIFF_DIFFERENT_DAY_NIGHT,
    CAPACITY_TARIFF_NONE,
    CAPACITY_TARIFF_SAME_DAY_NIGHT,
    DOMAIN,
    MODE_AUTO,
    MODE_PEAK_CHARGE,
)

from tests.const import MOCK_CONFIG_USER_TEMP1

# pylint: disable=unused-argument


async def test_current_peak_shaving_target1(
    hass: HomeAssistant,
    skip_service_calls,
    set_cet_timezone,
    freezer,
    mock_operation_settings_fetch_all_data,
):
    """Test Coordinator 2025-10-07."""

    mock_operation_settings_fetch_all_data(
        max_soc=90,
        discharge_threshold_w=6011,
        charge_threshold_w=0,
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
    freezer.move_to("2025-10-07T18:20:00+02:00")
    coordinator.primary_peak_shaving_target_w = 3005
    coordinator.secondary_peak_shaving_target_w = 6011
    coordinator.select_companion_mode = MODE_AUTO
    coordinator.operation_settings.override_active = False
    coordinator.operation_settings.discharge_threshold_w = 6011
    coordinator.operation_settings.charge_threshold_w = 0
    coordinator.operation_settings.original_discharge_threshold_w = (
        coordinator.operation_settings.discharge_threshold_w
    )
    coordinator.operation_settings.original_charge_threshold_w = (
        coordinator.operation_settings.charge_threshold_w
    )
    coordinator.switch_avoid_selling = False
    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_PEAK_CHARGE
    mode = await coordinator.operation_settings.get_original_mode()
    assert mode == MODE_PEAK_CHARGE
    assert coordinator.operation_settings.override_active is False
    assert coordinator.primary_peak_shaving_target_w == 3005
    assert coordinator.secondary_peak_shaving_target_w == 6011
    assert coordinator.capacity_tariff == CAPACITY_TARIFF_DIFFERENT_DAY_NIGHT

    # Verify different day and night targets
    coordinator.capacity_tariff = CAPACITY_TARIFF_DIFFERENT_DAY_NIGHT

    await coordinator.update_every_five_minutes()
    assert coordinator.sensor_current_peak_shaving_target.state == 3005

    freezer.move_to("2025-10-07T22:20:00+02:00")
    await coordinator.update_every_five_minutes()
    assert coordinator.sensor_current_peak_shaving_target.state == 6011

    # Verify same day and night targets
    coordinator.capacity_tariff = CAPACITY_TARIFF_SAME_DAY_NIGHT

    await coordinator.update_every_five_minutes()
    assert coordinator.sensor_current_peak_shaving_target.state == 3005

    freezer.move_to("2025-10-07T22:20:00+02:00")
    await coordinator.update_every_five_minutes()
    assert coordinator.sensor_current_peak_shaving_target.state == 3005

    # No tariffs
    coordinator.capacity_tariff = CAPACITY_TARIFF_NONE

    await coordinator.update_every_five_minutes()
    assert coordinator.sensor_current_peak_shaving_target.state == 0.0

    freezer.move_to("2025-10-07T22:20:00+02:00")
    await coordinator.update_every_five_minutes()
    assert coordinator.sensor_current_peak_shaving_target.state == 0.0

    # Unsubscribe to listeners
    coordinator.unsubscribe_listeners()
