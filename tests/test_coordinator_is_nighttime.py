"""Test ferro_ai_companion coordinator."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant

from custom_components.ferro_ai_companion.coordinator import (
    FerroAICompanionCoordinator,
)
from custom_components.ferro_ai_companion.const import (
    BUY_POWER_OFFSET,
    CAPACITY_TARIFF_DIFFERENT_DAY_NIGHT,
    CAPACITY_TARIFF_NONE,
    CAPACITY_TARIFF_SAME_DAY_NIGHT,
    DOMAIN,
    MODE_BUY,
    MODE_PEAK_CHARGE,
    MODE_PEAK_SELL,
    MODE_SELF,
    OVERRIDE_OFFSET,
)

# from custom_components.ferro_ai_companion.sensor import (
#     EVSmartChargingSensorCharging,
#     EVSmartChargingSensorStatus,
# )
from tests.const import MOCK_CONFIG_ALL

# pylint: disable=unused-argument


async def test_coordinator_is_nighttime(
    hass: HomeAssistant, skip_service_calls, set_cet_timezone, freezer, mock_operation_settings_fetch_all_data
):
    """Test Coordinator is_nighttime."""
    mock_operation_settings_fetch_all_data(
        max_soc=90,
        discharge_threshold_w=1000,
        charge_threshold_w=500,
        original_discharge_threshold_w=1000,
        original_charge_threshold_w=500,
    )

    freezer.move_to("2025-09-26T21:00:00+02:00")

    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG_ALL, entry_id="test")
    config_entry.add_to_hass(hass)
    coordinator = FerroAICompanionCoordinator(hass, config_entry)
    assert coordinator is not None
    await hass.async_block_till_done()

    # Set initial targets
    coordinator.primary_peak_shaving_target_w = 1000
    coordinator.secondary_peak_shaving_target_w = 2000

    coordinator.operation_settings.original_discharge_threshold_w = 1000
    coordinator.update_peak_shaving_targets()
    assert coordinator.primary_peak_shaving_target_w == 1000
    assert coordinator.secondary_peak_shaving_target_w == 2000

    coordinator.operation_settings.discharge_threshold_w = 1000
    coordinator.operation_settings.charge_threshold_w = 1000

    mode = await coordinator.operation_settings.get_mode()
    assert mode == MODE_BUY

    capacity_tariff = CAPACITY_TARIFF_NONE

    new_state = MODE_SELF
    await coordinator.operation_settings.override(
        new_state, coordinator.primary_peak_shaving_target_w, capacity_tariff
    )
    assert coordinator.operation_settings.discharge_threshold_w == 0 + OVERRIDE_OFFSET
    assert coordinator.operation_settings.charge_threshold_w == 0 + OVERRIDE_OFFSET

    new_state = MODE_PEAK_CHARGE
    await coordinator.operation_settings.override(
        new_state, coordinator.primary_peak_shaving_target_w, capacity_tariff
    )
    assert (
        coordinator.operation_settings.discharge_threshold_w
        == coordinator.primary_peak_shaving_target_w + OVERRIDE_OFFSET
    )
    assert coordinator.operation_settings.charge_threshold_w == 0 + OVERRIDE_OFFSET

    new_state = MODE_PEAK_SELL
    await coordinator.operation_settings.override(
        new_state, coordinator.primary_peak_shaving_target_w, capacity_tariff
    )
    assert (
        coordinator.operation_settings.discharge_threshold_w
        == coordinator.primary_peak_shaving_target_w + OVERRIDE_OFFSET
    )
    assert (
        coordinator.operation_settings.charge_threshold_w == -100000.0 + OVERRIDE_OFFSET
    )

    capacity_tariff = CAPACITY_TARIFF_NONE

    new_state = MODE_BUY
    await coordinator.operation_settings.override(
        new_state, coordinator.primary_peak_shaving_target_w, capacity_tariff
    )
    assert (
        coordinator.operation_settings.discharge_threshold_w
        == 100000.0 + OVERRIDE_OFFSET
    )
    assert (
        coordinator.operation_settings.charge_threshold_w == 100000.0 + OVERRIDE_OFFSET
    )

    capacity_tariff = CAPACITY_TARIFF_SAME_DAY_NIGHT

    await coordinator.operation_settings.override(
        new_state, coordinator.primary_peak_shaving_target_w, capacity_tariff
    )
    assert (
        coordinator.operation_settings.discharge_threshold_w
        == coordinator.primary_peak_shaving_target_w
        + OVERRIDE_OFFSET
        + BUY_POWER_OFFSET
    )
    assert (
        coordinator.operation_settings.charge_threshold_w
        == coordinator.primary_peak_shaving_target_w
        + OVERRIDE_OFFSET
        + BUY_POWER_OFFSET
    )

    capacity_tariff = CAPACITY_TARIFF_DIFFERENT_DAY_NIGHT

    freezer.move_to("2025-09-26T21:59:00+02:00")
    await coordinator.operation_settings.override(
        new_state, coordinator.primary_peak_shaving_target_w, capacity_tariff
    )
    assert (
        coordinator.operation_settings.discharge_threshold_w
        == coordinator.primary_peak_shaving_target_w
        + OVERRIDE_OFFSET
        + BUY_POWER_OFFSET
    )
    assert (
        coordinator.operation_settings.charge_threshold_w
        == coordinator.primary_peak_shaving_target_w
        + OVERRIDE_OFFSET
        + BUY_POWER_OFFSET
    )

    freezer.move_to("2025-09-26T22:01:00+02:00")
    await coordinator.operation_settings.update_override(
        new_state, coordinator.primary_peak_shaving_target_w, capacity_tariff
    )
    assert (
        coordinator.operation_settings.discharge_threshold_w
        == coordinator.primary_peak_shaving_target_w * 2.0
        + OVERRIDE_OFFSET
        + BUY_POWER_OFFSET
    )
    assert (
        coordinator.operation_settings.charge_threshold_w
        == coordinator.primary_peak_shaving_target_w * 2.0
        + OVERRIDE_OFFSET
        + BUY_POWER_OFFSET
    )

    freezer.move_to("2025-09-27T05:59:00+02:00")
    await coordinator.operation_settings.update_override(
        new_state, coordinator.primary_peak_shaving_target_w, capacity_tariff
    )
    assert (
        coordinator.operation_settings.discharge_threshold_w
        == coordinator.primary_peak_shaving_target_w * 2.0
        + OVERRIDE_OFFSET
        + BUY_POWER_OFFSET
    )
    assert (
        coordinator.operation_settings.charge_threshold_w
        == coordinator.primary_peak_shaving_target_w * 2.0
        + OVERRIDE_OFFSET
        + BUY_POWER_OFFSET
    )

    freezer.move_to("2025-09-27T06:01:00+02:00")
    await coordinator.operation_settings.update_override(
        new_state, coordinator.primary_peak_shaving_target_w, capacity_tariff
    )
    assert (
        coordinator.operation_settings.discharge_threshold_w
        == coordinator.primary_peak_shaving_target_w
        + OVERRIDE_OFFSET
        + BUY_POWER_OFFSET
    )
    assert (
        coordinator.operation_settings.charge_threshold_w
        == coordinator.primary_peak_shaving_target_w
        + OVERRIDE_OFFSET
        + BUY_POWER_OFFSET
    )

    # Unsubscribe to listeners
    coordinator.unsubscribe_listeners()
