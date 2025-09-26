"""Constants for ferro_ai_companion tests."""

from custom_components.ferro_ai_companion.const import (
    CAPACITY_TARIFF_DIFFERENT_DAY_NIGHT,
    CONF_CAPACITY_TARIFF,
    CONF_DEVICE_NAME,
    CONF_EV_SOC_SENSOR,
    CONF_EV_TARGET_SOC_SENSOR,
    CONF_MQTT_ENTITY,
    CONF_NUMBER_OF_PHASES,
    CONF_SETTINGS_ENTITY,
    CONF_SOLAR_EV_CHARGING_ENABLED,
    CONF_SOLAR_FORECAST_TODAY_REMAINING,
    NAME,
)

# Mock config data to be used across multiple tests
MOCK_CONFIG_USER = {
    CONF_SETTINGS_ENTITY: "sensor.ferroamp_operation_settting_any",
    CONF_MQTT_ENTITY: "sensor.ferroamp_any",
    CONF_CAPACITY_TARIFF: CAPACITY_TARIFF_DIFFERENT_DAY_NIGHT,
}

MOCK_CONFIG_USER_TEMP1 = {
    CONF_SETTINGS_ENTITY: "sensor.ferroamp_operation_settting_any",
    CONF_MQTT_ENTITY: "sensor.ferroamp_any",
    CONF_CAPACITY_TARIFF: CAPACITY_TARIFF_DIFFERENT_DAY_NIGHT,
    CONF_SOLAR_EV_CHARGING_ENABLED: False,
}

MOCK_CONFIG_USER_EXTRA = {
    CONF_DEVICE_NAME: NAME,
    CONF_SETTINGS_ENTITY: "sensor.ferroamp_operation_settting_any",
    CONF_MQTT_ENTITY: "sensor.ferroamp_any",
    CONF_CAPACITY_TARIFF: CAPACITY_TARIFF_DIFFERENT_DAY_NIGHT,
    CONF_SOLAR_EV_CHARGING_ENABLED: False,
}


MOCK_CONFIG_ALL = {
    CONF_SETTINGS_ENTITY: "sensor.ferroamp_operation_settting_any",
    CONF_MQTT_ENTITY: "sensor.ferroamp_any",
    CONF_CAPACITY_TARIFF: "different_day_night",
    CONF_SOLAR_EV_CHARGING_ENABLED: True,
    CONF_SOLAR_FORECAST_TODAY_REMAINING: "switch.ocpp_charge_control",
    CONF_EV_SOC_SENSOR: "sensor.volkswagen_we_connect_id_state_of_charge",
    CONF_EV_TARGET_SOC_SENSOR: "sensor.volkswagen_we_connect_id_target_state_of_charge",
    CONF_NUMBER_OF_PHASES: 3,
}

MOCK_CONFIG_ALL_V1 = {
    CONF_SETTINGS_ENTITY: "sensor.ferroamp_operation_settting_any",
    CONF_MQTT_ENTITY: "sensor.ferroamp_any",
    CONF_SOLAR_EV_CHARGING_ENABLED: False,
    CONF_SOLAR_FORECAST_TODAY_REMAINING: "switch.ocpp_charge_control",
    CONF_EV_SOC_SENSOR: "sensor.volkswagen_we_connect_id_state_of_charge",
    CONF_EV_TARGET_SOC_SENSOR: "sensor.volkswagen_we_connect_id_target_state_of_charge",
    CONF_NUMBER_OF_PHASES: 3,
}

MOCK_CONFIG_ALL_V2 = {
    CONF_SETTINGS_ENTITY: "sensor.ferroamp_operation_settting_any",
    CONF_MQTT_ENTITY: "sensor.ferroamp_any",
    CONF_CAPACITY_TARIFF: "different_day_night",
    CONF_SOLAR_EV_CHARGING_ENABLED: False,
    CONF_SOLAR_FORECAST_TODAY_REMAINING: "switch.ocpp_charge_control",
    CONF_EV_SOC_SENSOR: "sensor.volkswagen_we_connect_id_state_of_charge",
    CONF_EV_TARGET_SOC_SENSOR: "sensor.volkswagen_we_connect_id_target_state_of_charge",
    CONF_NUMBER_OF_PHASES: 3,
}
