from __future__ import annotations

from enum import Enum
import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.components import binary_sensor, sensor
from homeassistant.const import (
    CONF_DEVICE_CLASS,
    CONF_ICON,
    CONF_NAME,
    CONF_UNIT_OF_MEASUREMENT,
    Platform,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import (
    CONF_ATTRIBUTES,
    CONF_ENTITY_PLATFORM,
    CONF_FORCE_UPDATE,
    CONF_RESTORE,
    CONF_VALUE,
    CONF_VALUE_TYPE,
    CONF_VARIABLE_ID,
    DEFAULT_FORCE_UPDATE,
    DEFAULT_ICON,
    DEFAULT_RESTORE,
    DOMAIN,
    PLATFORMS,
)
from .helpers import value_to_type

# sensor: SensorDeviceClass, DEVICE_CLASS_STATE_CLASSES, DEVICE_CLASS_UNITS
# binary_sensor: BinarySensorDeviceClass

_LOGGER = logging.getLogger(__name__)

COMPONENT_CONFIG_URL = "https://github.com/Wibias/hass-variables"

# Note the input displayed to the user will be translated. See the
# translations/<lang>.json file and strings.json. See here for further information:
# https://developers.home-assistant.io/docs/config_entries_config_flow_handler/#translations

SENSOR_DEVICE_CLASS_SELECT_LIST = []
SENSOR_DEVICE_CLASS_SELECT_LIST.append(
    selector.SelectOptionDict(label="None", value="None")
)
for el in sensor.SensorDeviceClass:
    SENSOR_DEVICE_CLASS_SELECT_LIST.append(
        selector.SelectOptionDict(label=str(el.name), value=str(el.value))
    )

BINARY_SENSOR_DEVICE_CLASS_SELECT_LIST = []
BINARY_SENSOR_DEVICE_CLASS_SELECT_LIST.append(
    selector.SelectOptionDict(label="None", value="None")
)
for el in binary_sensor.BinarySensorDeviceClass:
    BINARY_SENSOR_DEVICE_CLASS_SELECT_LIST.append(
        selector.SelectOptionDict(label=str(el.name), value=str(el.value))
    )

ADD_SENSOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_VARIABLE_ID): cv.string,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_ICON, default=DEFAULT_ICON): selector.IconSelector(
            selector.IconSelectorConfig()
        ),
        vol.Optional(CONF_DEVICE_CLASS): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=SENSOR_DEVICE_CLASS_SELECT_LIST,
                multiple=False,
                custom_value=False,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Optional(CONF_RESTORE, default=DEFAULT_RESTORE): selector.BooleanSelector(
            selector.BooleanSelectorConfig()
        ),
        vol.Optional(
            CONF_FORCE_UPDATE, default=DEFAULT_FORCE_UPDATE
        ): selector.BooleanSelector(selector.BooleanSelectorConfig()),
    }
)

ADD_BINARY_SENSOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_VARIABLE_ID): cv.string,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_ICON, default=DEFAULT_ICON): selector.IconSelector(
            selector.IconSelectorConfig()
        ),
        vol.Optional(CONF_VALUE): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=["true", "false"],
                translation_key="boolean_options",
                multiple=False,
                custom_value=False,
                mode=selector.SelectSelectorMode.LIST,
            )
        ),
        vol.Optional(CONF_ATTRIBUTES): selector.ObjectSelector(
            selector.ObjectSelectorConfig()
        ),
        vol.Optional(CONF_DEVICE_CLASS): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=BINARY_SENSOR_DEVICE_CLASS_SELECT_LIST,
                multiple=False,
                custom_value=False,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Optional(CONF_RESTORE, default=DEFAULT_RESTORE): selector.BooleanSelector(
            selector.BooleanSelectorConfig()
        ),
        vol.Optional(
            CONF_FORCE_UPDATE, default=DEFAULT_FORCE_UPDATE
        ): selector.BooleanSelector(selector.BooleanSelectorConfig()),
    }
)


async def validate_sensor_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input"""

    # _LOGGER.debug(f"[config_flow validate_sensor_input] data: {data}")
    if data.get(CONF_NAME):
        return {"title": data.get(CONF_NAME)}
    else:
        return {"title": data.get(CONF_VARIABLE_ID, "")}


class VariableConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    # Connection classes in homeassistant/config_entries.py are now deprecated

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""

        return self.async_show_menu(
            step_id="user",
            menu_options=["add_" + p for p in PLATFORMS],
        )

    async def async_step_add_sensor(self, user_input=None, errors=None):
        if user_input is not None:
            user_input.update({CONF_ENTITY_PLATFORM: Platform.SENSOR})
            try:
                _LOGGER.debug(f"[New Sensor Page 1] page_1_input: {user_input}")
                self.add_sensor_input = user_input
                return await self.async_step_sensor_page_2()
            except Exception as err:
                _LOGGER.exception(
                    f"[config_flow async_step_add_sensor] Unexpected exception: {err}"
                )
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="add_sensor",
            data_schema=ADD_SENSOR_SCHEMA,
            errors=errors,
            description_placeholders={
                "component_config_url": COMPONENT_CONFIG_URL,
            },
        )

    async def async_step_sensor_page_2(self, user_input=None):
        errors = {}
        if user_input is not None:
            _LOGGER.debug(f"[New Sensor Page 2] page_1_input: {self.add_sensor_input}")
            _LOGGER.debug(f"[New Sensor Page 2] page_2_input: {user_input}")

            try:
                newval = value_to_type(
                    user_input.get(CONF_VALUE),
                    self.add_sensor_input.get(CONF_VALUE_TYPE),
                )
            except ValueError:
                errors["base"] = "invalid_value_type"
            else:
                user_input[CONF_VALUE] = newval

            _LOGGER.debug(
                f"[New Sensor Page 2] value_type: {self.add_sensor_input.get(CONF_VALUE_TYPE)}"
            )
            _LOGGER.debug(
                f"[New Sensor Page 2] type of value: {type(user_input.get(CONF_VALUE))}"
            )

            if not errors:
                if self.add_sensor_input is not None and self.add_sensor_input:
                    user_input.update(self.add_sensor_input)
                if user_input is not None:
                    for k, v in list(user_input.items()):
                        if v is None or v == "None":
                            user_input.pop(k, None)
                _LOGGER.debug(f"[New Sensor Page 2] Final user_input: {user_input}")
                info = await validate_sensor_input(self.hass, user_input)
                _LOGGER.debug(f"[New Sensor Variable] info: {info}")
                return self.async_create_entry(
                    title=info.get("title", ""), data=user_input
                )

        _LOGGER.debug(f"[New Sensor Page 2] Initial user_input: {user_input}")
        _LOGGER.debug(
            f"[New Sensor Page 2] device_class: {self.add_sensor_input.get(CONF_DEVICE_CLASS)}"
        )

        SENSOR_STATE_CLASS_SELECT_LIST = []
        SENSOR_STATE_CLASS_SELECT_LIST.append(
            selector.SelectOptionDict(label="None", value="None")
        )
        SENSOR_UNITS_SELECT_LIST = []
        SENSOR_UNITS_SELECT_LIST.append(
            selector.SelectOptionDict(label="None", value="None")
        )

        SENSOR_PAGE_2_SCHEMA = vol.Schema({})
        if (
            self.add_sensor_input.get(CONF_DEVICE_CLASS) is not None
            and self.add_sensor_input.get(CONF_DEVICE_CLASS) != "None"
        ):
            for el in sensor.DEVICE_CLASS_STATE_CLASSES.get(
                self.add_sensor_input.get(CONF_DEVICE_CLASS), Enum
            ):
                SENSOR_STATE_CLASS_SELECT_LIST.append(
                    selector.SelectOptionDict(label=str(el.name), value=str(el.value))
                )
            for el in sensor.DEVICE_CLASS_UNITS.get(
                self.add_sensor_input.get(CONF_DEVICE_CLASS), []
            ):
                SENSOR_UNITS_SELECT_LIST.append(
                    selector.SelectOptionDict(label=str(el), value=str(el))
                )

            if self.add_sensor_input.get(CONF_DEVICE_CLASS) in [
                sensor.SensorDeviceClass.DATE
            ]:
                SENSOR_PAGE_2_SCHEMA = SENSOR_PAGE_2_SCHEMA.extend(
                    {
                        vol.Optional(CONF_VALUE): selector.DateSelector(
                            selector.DateSelectorConfig()
                        )
                    }
                )
                value_type = "date"
            elif self.add_sensor_input.get(CONF_DEVICE_CLASS) in [
                sensor.SensorDeviceClass.TIMESTAMP
            ]:
                SENSOR_PAGE_2_SCHEMA = SENSOR_PAGE_2_SCHEMA.extend(
                    {
                        vol.Optional(CONF_VALUE): selector.DateTimeSelector(
                            selector.DateTimeSelectorConfig()
                        )
                    }
                )
                value_type = "datetime"
            else:
                SENSOR_PAGE_2_SCHEMA = SENSOR_PAGE_2_SCHEMA.extend(
                    {
                        vol.Optional(CONF_VALUE): selector.TextSelector(
                            selector.TextSelectorConfig()
                        )
                    }
                )
                value_type = "number"
        else:
            for el in sensor.SensorStateClass:
                SENSOR_STATE_CLASS_SELECT_LIST.append(
                    selector.SelectOptionDict(label=str(el.name), value=str(el.value))
                )

            SENSOR_PAGE_2_SCHEMA = SENSOR_PAGE_2_SCHEMA.extend(
                {
                    vol.Optional(CONF_VALUE): selector.TextSelector(
                        selector.TextSelectorConfig()
                    )
                }
            )
            value_type = "string"

        _LOGGER.debug(
            f"[New Sensor Page 2] SENSOR_STATE_CLASS_SELECT_LIST: {SENSOR_STATE_CLASS_SELECT_LIST}"
        )
        _LOGGER.debug(
            f"[New Sensor Page 2] SENSOR_UNITS_SELECT_LIST: {SENSOR_UNITS_SELECT_LIST}"
        )

        SENSOR_PAGE_2_SCHEMA = SENSOR_PAGE_2_SCHEMA.extend(
            {
                vol.Optional(CONF_ATTRIBUTES): selector.ObjectSelector(
                    selector.ObjectSelectorConfig()
                )
            }
        )
        if len(SENSOR_STATE_CLASS_SELECT_LIST) > 1:
            SENSOR_PAGE_2_SCHEMA = SENSOR_PAGE_2_SCHEMA.extend(
                {
                    vol.Optional(sensor.CONF_STATE_CLASS): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=SENSOR_STATE_CLASS_SELECT_LIST,
                            multiple=False,
                            custom_value=False,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    )
                }
            )

        if len(SENSOR_UNITS_SELECT_LIST) > 1:
            SENSOR_PAGE_2_SCHEMA = SENSOR_PAGE_2_SCHEMA.extend(
                {
                    vol.Optional(CONF_UNIT_OF_MEASUREMENT): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=SENSOR_UNITS_SELECT_LIST,
                            multiple=False,
                            custom_value=False,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    )
                }
            )
        if user_input is None:
            user_input = {}
        _LOGGER.debug(f"[New Sensor Page 2] value_type: {value_type}")
        self.add_sensor_input.update({CONF_VALUE_TYPE: value_type})
        if self.add_sensor_input.get(CONF_NAME) is None or self.add_sensor_input.get(
            CONF_NAME
        ) == self.add_sensor_input.get(CONF_VARIABLE_ID):
            disp_name = self.add_sensor_input.get(CONF_VARIABLE_ID)
        else:
            disp_name = f"{self.add_sensor_input.get(CONF_NAME)} ({self.add_sensor_input.get(CONF_VARIABLE_ID)})"
        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="sensor_page_2",
            data_schema=SENSOR_PAGE_2_SCHEMA,
            errors=errors,
            description_placeholders={
                "device_class": self.add_sensor_input.get(CONF_DEVICE_CLASS, "None"),
                "disp_name": disp_name,
                "value_type": value_type,
            },
        )

    async def async_step_add_binary_sensor(self, user_input=None, errors=None):
        if user_input is not None:

            try:
                user_input.update({CONF_ENTITY_PLATFORM: Platform.BINARY_SENSOR})
                info = await validate_sensor_input(self.hass, user_input)
                _LOGGER.debug(f"[New Binary Sensor Variable] info: {info}")
                _LOGGER.debug(f"[Sensor Options] updated user_input: {user_input}")
                return self.async_create_entry(
                    title=info.get("title", ""), data=user_input
                )
            except Exception as err:
                _LOGGER.exception(
                    f"[config_flow async_step_add_binary_sensor] Unexpected exception: {err}"
                )
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="add_binary_sensor",
            data_schema=ADD_BINARY_SENSOR_SCHEMA,
            errors=errors,
            description_placeholders={
                "component_config_url": COMPONENT_CONFIG_URL,
            },
        )

    # this is run to import the configuration.yaml parameters\
    async def async_step_import(self, import_config=None) -> FlowResult:
        """Import a config entry from configuration.yaml."""

        # _LOGGER.debug(f"[async_step_import] import_config: {import_config)}")
        return await self.async_step_add_sensor(import_config)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ):
        """Get the options flow."""
        return VariableOptionsFlowHandler(config_entry)


class VariableOptionsFlowHandler(config_entries.OptionsFlow):
    """Options for the component."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Init object."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""

        # _LOGGER.debug("Starting Options")
        # _LOGGER.debug(f"[Options] initial config: {self.config_entry.data)}")
        # _LOGGER.debug(f"[Options] initial options: {self.config_entry.options)}")

        if self.config_entry.data.get(CONF_ENTITY_PLATFORM) in PLATFORMS and (
            new_func := getattr(
                self,
                "async_step_"
                + self.config_entry.data.get(CONF_ENTITY_PLATFORM)
                + "_options",
                False,
            )
        ):
            return await new_func()

    async def async_step_sensor_options(
        self, user_input=None, errors=None
    ) -> FlowResult:

        if user_input is not None:
            _LOGGER.debug(f"[Sensor Options] user_input: {user_input}")

            for m in dict(self.config_entry.data).keys():
                user_input.setdefault(m, self.config_entry.data[m])
            _LOGGER.debug(f"[Sensor Options] updated user_input: {user_input}")
            self.config_entry.options = {}

            self.hass.config_entries.async_update_entry(
                self.config_entry, data=user_input, options=self.config_entry.options
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data=user_input)

        SENSOR_OPTIONS_SCHEMA = vol.Schema(
            {
                vol.Optional(
                    CONF_VALUE, default=self.config_entry.data.get(CONF_VALUE)
                ): cv.string,
                vol.Optional(
                    CONF_ATTRIBUTES, default=self.config_entry.data.get(CONF_ATTRIBUTES)
                ): selector.ObjectSelector(selector.ObjectSelectorConfig()),
                vol.Optional(
                    CONF_RESTORE,
                    default=self.config_entry.data.get(CONF_RESTORE, DEFAULT_RESTORE),
                ): selector.BooleanSelector(selector.BooleanSelectorConfig()),
                vol.Optional(
                    CONF_FORCE_UPDATE,
                    default=self.config_entry.data.get(
                        CONF_FORCE_UPDATE, DEFAULT_FORCE_UPDATE
                    ),
                ): selector.BooleanSelector(selector.BooleanSelectorConfig()),
            }
        )

        return self.async_show_form(
            step_id="sensor_options",
            data_schema=SENSOR_OPTIONS_SCHEMA,
            description_placeholders={
                "component_config_url": COMPONENT_CONFIG_URL,
                "entity_name": self.config_entry.data.get(
                    CONF_NAME, self.config_entry.data.get(CONF_VARIABLE_ID)
                ),
            },
        )

    async def async_step_binary_sensor_options(
        self, user_input=None, errors=None
    ) -> FlowResult:

        if user_input is not None:
            _LOGGER.debug(f"[Binary Sensor Options] user_input: {user_input}")
            for m in dict(self.config_entry.data).keys():
                user_input.setdefault(m, self.config_entry.data[m])
            _LOGGER.debug(f"[Binary Sensor Options] updated user_input: {user_input}")
            self.config_entry.options = {}

            self.hass.config_entries.async_update_entry(
                self.config_entry, data=user_input, options=self.config_entry.options
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data=user_input)

        BINARY_SENSOR_OPTIONS_SCHEMA = vol.Schema(
            {
                vol.Optional(
                    CONF_VALUE,
                    default=self.config_entry.data.get(CONF_VALUE),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=["true", "false"],
                        translation_key="boolean_options",
                        multiple=False,
                        custom_value=False,
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
                vol.Optional(
                    CONF_ATTRIBUTES, default=self.config_entry.data.get(CONF_ATTRIBUTES)
                ): selector.ObjectSelector(selector.ObjectSelectorConfig()),
                vol.Optional(
                    CONF_RESTORE,
                    default=self.config_entry.data.get(CONF_RESTORE, DEFAULT_RESTORE),
                ): selector.BooleanSelector(selector.BooleanSelectorConfig()),
                vol.Optional(
                    CONF_FORCE_UPDATE,
                    default=self.config_entry.data.get(
                        CONF_FORCE_UPDATE, DEFAULT_FORCE_UPDATE
                    ),
                ): selector.BooleanSelector(selector.BooleanSelectorConfig()),
            }
        )

        return self.async_show_form(
            step_id="binary_sensor_options",
            data_schema=BINARY_SENSOR_OPTIONS_SCHEMA,
            description_placeholders={
                "component_config_url": COMPONENT_CONFIG_URL,
                "entity_name": self.config_entry.data.get(
                    CONF_NAME, self.config_entry.data.get(CONF_VARIABLE_ID)
                ),
            },
        )
