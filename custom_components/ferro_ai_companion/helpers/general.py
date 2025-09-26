"""General helpers"""

# pylint: disable=relative-beyond-top-level
import logging
from typing import Any
from datetime import time
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import State
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)


class Validator:
    """Validator"""

    @staticmethod
    def is_float(element: Any) -> bool:
        """Check that argument is a float"""
        try:
            float(element)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    @staticmethod
    def is_soc_state(soc_state: State) -> bool:
        """Check that argument is a SOC state"""
        if soc_state is not None:
            if soc_state.state != "unavailable":
                soc = soc_state.state
                if not Validator.is_float(soc):
                    return False
                if 0.0 <= float(soc) <= 100.0:
                    return True
        return False


def get_parameter(config_entry: ConfigEntry, parameter: str, default_val: Any = None):
    """Get parameter from OptionsFlow or ConfigFlow"""
    if parameter in config_entry.options.keys():
        return config_entry.options.get(parameter)
    if parameter in config_entry.data.keys():
        return config_entry.data.get(parameter)
    return default_val


def is_nighttime():
    """Check if it's night"""
    # Get the current local time (timezone-aware)
    now = dt_util.now()

    # Define the start and end times
    start_time = time(22, 0)  # 22:00
    end_time = time(6, 0)     # 06:00

    # Check if current time is between start_time and end_time
    if start_time <= end_time:
        # Case: tart_time and end_time are same day
        return start_time <= now.time() <= end_time
    else:
        # Case: tart_time and end_time are different days
        return now.time() >= start_time or now.time() <= end_time
