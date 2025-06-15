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
ICON_LIST = "mdi:format-list-bulleted"

# Platforms
SENSOR = Platform.SENSOR
SWITCH = Platform.SWITCH
NUMBER = Platform.NUMBER
SELECT = Platform.SELECT
PLATFORMS = [SENSOR, SWITCH, NUMBER, SELECT]
PLATFORM_FERROAMP_OPERATION_SETTINGS = "ferroamp_operation_settings"
PLATFORM_FERROAMP = "ferroamp"
PLATFORM_FORECAST_SOLAR = "forecast_solar"
PLATFORM_VW = "volkswagen_we_connect_id"

# Entity keys
ENTITY_KEY_CONF_ASSUMED_HOUSE_CONSUMPTION_NUMBER = "assumed_house_consumption"
ENTITY_KEY_CONF_MAX_CHARGING_CURRENT_NUMBER = "max_charging_current"
ENTITY_KEY_CONF_MIN_CHARGING_CURRENT_NUMBER = "min_charging_current"

ENTITY_KEY_MODE_SENSOR = "energyhub_mode"
ENTITY_KEY_ORIGINAL_MODE_SENSOR = "ferro_ai_mode"
ENTITY_KEY_PEAK_SHAVING_TARGET_SENSOR = "peak_shaving_target"
ENTITY_KEY_SECONDARY_PEAK_SHAVING_TARGET_SENSOR = "secondary_peak_shaving_target"
ENTITY_KEY_SOLAR_EV_CHARGING_SENSOR = "solar_ev_charging"
ENTITY_KEY_CHARGING_CURRENT_SENSOR = "charging_current"

ENTITY_KEY_EV_CONNECTED_SWITCH = "ev_connected"
ENTITY_KEY_AVOID_IMPORT_SWITCH = "avoid_import"
ENTITY_KEY_AVOID_BATTERY_USAGE_SWITCH = "avoid_battery_usage"
ENTITY_KEY_FORCE_BUYING_SWITCH = "force_buying"
ENTITY_KEY_FORCE_SELLING_SWITCH = "force_selling"

ENTITY_KEY_COMPANION_MODE_SELECT = "companion_mode"

# Configuration and options
CONF_DEVICE_NAME = "device_name"
CONF_SETTINGS_ENTITY = "settings_entity"
CONF_MQTT_ENTITY = "mqtt_entity"
CONF_SOLAR_EV_CHARGING_ENABLED = "solar_ev_charging_enabled"
CONF_SOLAR_FORECAST_TODAY_REMAINING = "solar_forecast_today_remaining"
CONF_EV_SOC_SENSOR = "ev_soc_sensor"
CONF_EV_TARGET_SOC_SENSOR = "ev_target_soc_sensor"
CONF_NUMBER_OF_PHASES = "number_of_phases"

MODE_AUTO = "auto"
MODE_SELF = "self"
MODE_PEAK_CHARGE = "peak_charge"
MODE_PEAK_SELL = "peak_sell"
MODE_BUY = "buy"
MODE_SELL = "sell"
MODE_UNKNOWN = "unknown"

# Ferro AI modes
FERRO_AI_MODES = [
    MODE_SELF,
    MODE_PEAK_CHARGE,
    MODE_PEAK_SELL,
    MODE_BUY,
    MODE_SELL,
    MODE_UNKNOWN,
]
# Companion modes
COMPANION_MODES = [
    MODE_AUTO,
    MODE_SELF,
    MODE_PEAK_CHARGE,
    MODE_PEAK_SELL,
    MODE_BUY,
    MODE_SELL,
]

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
