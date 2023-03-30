from __future__ import annotations

import datetime
import logging

_LOGGER = logging.getLogger(__name__)


def to_num(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return None


def value_to_type(init_str, value_type):

    if init_str is None or (
        isinstance(init_str, str)
        and init_str.lower() in ["", "none", "unknown", "unavailable"]
    ):
        _LOGGER.debug(f"[value_to_type] value: {init_str}, returning None")
        return None

    elif value_type == "date":
        try:
            value_date = datetime.date.fromisoformat(init_str)
        except ValueError:
            raise ValueError(f"Cannot convert string to {value_type}: {init_str}")
            return None
        else:
            _LOGGER.debug(f"[value_to_type] date value: |{value_date}|")
            return value_date

    elif value_type == "datetime":
        try:
            value_datetime = datetime.datetime.fromisoformat(init_str)
        except ValueError:
            raise ValueError(f"Cannot convert string to {value_type}: {init_str}")
            return None
        else:
            _LOGGER.debug(f"[value_to_type] datetime value: |{value_datetime}|")
            return value_datetime

    elif value_type == "number":
        if (value_num := to_num(init_str)) is not None:
            _LOGGER.debug(f"[value_to_type] number value: |{value_num}|")
            return value_num
        else:
            raise ValueError(f"Cannot convert string to {value_type}: {init_str}")
    elif value_type == "string":
        _LOGGER.debug(f"[value_to_type] stringvalue: |{init_str}|")
        return init_str
    else:
        raise ValueError(f"Invalid value_type: {value_type}")
        return None
