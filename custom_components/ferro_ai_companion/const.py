"""Constants file"""

from homeassistant.const import Platform
from homeassistant.const import __version__ as HA_VERSION

NAME = "Ferro AI Companion"
DOMAIN = "ferro_ai_companion"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.1.0"
ISSUE_URL = "https://github.com/jonasbkarlsson/ferro_ai_companion/issues"

# Icons
ICON = "mdi:flash"
ICON_BATTERY_50 = "mdi:battery-50"
ICON_CONNECTION = "mdi:connection"
ICON_CHARGING = "mdi:battery-charging-30"

# Platforms
SENSOR = Platform.SENSOR
SWITCH = Platform.SWITCH
NUMBER = Platform.NUMBER
PLATFORMS = [SENSOR, SWITCH, NUMBER]
PLATFORM_FERROAMP_OPERATION_SETTINGS = "ferroamp_operation_settings"
PLATFORM_FERROAMP = "ferroamp"
PLATFORM_FORECAST_SOLAR = "forecast_solar"
PLATFORM_VW = "volkswagen_we_connect_id"

# Entity keys
ENTITY_KEY_CONF_ASSUMED_HOUSE_CONSUMPTION_NUMBER = "assumed_house_consumption"
ENTITY_KEY_CONF_MAX_CHARGING_CURRENT_NUMBER = "max_charging_current"
ENTITY_KEY_CONF_MIN_CHARGING_CURRENT_NUMBER = "min_charging_current"

ENTITY_KEY_MODE_SENSOR = "mode"
ENTITY_KEY_ORIGINAL_MODE_SENSOR = "original_mode"
ENTITY_KEY_PEAK_SHAVING_TARGET_SENSOR = "peak_shaving_target"
ENTITY_KEY_SECONDARY_PEAK_SHAVING_TARGET_SENSOR = "secondary_peak_shaving_target"
ENTITY_KEY_SOLAR_EV_CHARGING_SENSOR = "solar_ev_charging"
ENTITY_KEY_CHARGING_CURRENT_SENSOR = "charging_current"

ENTITY_KEY_EV_CONNECTED_SWITCH = "ev_connected"

# Configuration and options
CONF_DEVICE_NAME = "device_name"
CONF_SETTINGS_ENTITY = "settings_entity"
CONF_MQTT_ENTITY = "mqtt_entity"
CONF_SOLAR_EV_CHARGING_ENABLED = "solar_ev_charging_enabled"
CONF_SOLAR_FORECAST_TODAY_REMAINING = "solar_forecast_today_remaining"
CONF_EV_SOC_SENSOR = "ev_soc_sensor"
CONF_EV_TARGET_SOC_SENSOR = "ev_target_soc_sensor"
CONF_NUMBER_OF_PHASES = "number_of_phases"

MODE_SELF = "self"
MODE_PEAK_SHAVING = "peak_shaving"
MODE_BUY = "buy"
MODE_SELL = "sell"
MODE_UNKNOWN = "unknown"

# Defaults
DEFAULT_NAME = DOMAIN
DEFAULT_TARGET_SOC = 100

DEBUG = False

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
Home Assistant: {HA_VERSION}
-------------------------------------------------------------------
"""
