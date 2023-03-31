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

    if value_type == "date":
        if init_str is None:
            return None
        else:
            try:
                valdate = datetime.date.fromisoformat(init_str)
            except ValueError:
                raise ValueError(f"Cannot convert string to {value_type}: {init_str}")
                return None
            else:
                _LOGGER.debug(f"[value_to_type] date value: |{valdate}|")
                return valdate

    elif value_type == "datetime":
        if init_str is None:
            return None
        else:
            try:
                valdatetime = datetime.datetime.fromisoformat(init_str)
            except ValueError:
                raise ValueError(f"Cannot convert string to {value_type}: {init_str}")
                return None
            else:
                _LOGGER.debug(f"[value_to_type] datetime value: |{valdatetime}|")
                return valdatetime

    elif value_type == "number":
        if init_str is None:
            return None
        elif (valnum := to_num(init_str)) is not None:
            _LOGGER.debug(f"[value_to_type] number value: |{valnum}|")
            return valnum
        else:
            raise ValueError(f"Cannot convert string to {value_type}: {init_str}")
    elif value_type == "string":
        _LOGGER.debug(f"[value_to_type] stringvalue: |{init_str}|")
        return init_str
    else:
        raise ValueError(f"Invalid value_type: {value_type}")
        return None
