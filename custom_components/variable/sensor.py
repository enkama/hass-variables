from collections.abc import MutableMapping
import copy
import logging

from homeassistant.components.recorder import DATA_INSTANCE as RECORDER_INSTANCE
from homeassistant.components.sensor import (
    CONF_STATE_CLASS,
    PLATFORM_SCHEMA,
    RestoreSensor,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_FRIENDLY_NAME,
    ATTR_ICON,
    CONF_DEVICE_CLASS,
    CONF_ICON,
    CONF_NAME,
    CONF_UNIT_OF_MEASUREMENT,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util import slugify
import voluptuous as vol

from .const import (
    ATTR_ATTRIBUTES,
    ATTR_REPLACE_ATTRIBUTES,
    ATTR_VALUE,
    CONF_ATTRIBUTES,
    CONF_EXCLUDE_FROM_RECORDER,
    CONF_FORCE_UPDATE,
    CONF_RESTORE,
    CONF_VALUE,
    CONF_VALUE_TYPE,
    CONF_VARIABLE_ID,
    CONF_YAML_VARIABLE,
    DEFAULT_EXCLUDE_FROM_RECORDER,
    DEFAULT_FORCE_UPDATE,
    DEFAULT_ICON,
    DEFAULT_REPLACE_ATTRIBUTES,
    DEFAULT_RESTORE,
    DOMAIN,
)
from .helpers import value_to_type

_LOGGER = logging.getLogger(__name__)

PLATFORM = Platform.SENSOR
ENTITY_ID_FORMAT = PLATFORM + ".{}"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_VARIABLE_ID): cv.string,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_ICON, default=DEFAULT_ICON): cv.string,
        vol.Optional(CONF_VALUE): cv.match_all,
        vol.Optional(CONF_ATTRIBUTES): dict,
        vol.Optional(CONF_RESTORE, default=DEFAULT_RESTORE): cv.boolean,
        vol.Optional(CONF_FORCE_UPDATE, default=DEFAULT_FORCE_UPDATE): cv.boolean,
        vol.Optional(
            CONF_EXCLUDE_FROM_RECORDER, default=DEFAULT_EXCLUDE_FROM_RECORDER
        ): cv.boolean,
    }
)

SERVICE_UPDATE_VARIABLE = "update_" + PLATFORM

VARIABLE_ATTR_SETTINGS = {ATTR_FRIENDLY_NAME: "_attr_name", ATTR_ICON: "_attr_icon"}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities,
) -> None:

    """Setup the Sensor Variable entity with a config_entry (config_flow)."""

    config_entry.options = {}
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_UPDATE_VARIABLE,
        {
            vol.Optional(ATTR_VALUE): cv.string,
            vol.Optional(ATTR_ATTRIBUTES): dict,
            vol.Optional(
                ATTR_REPLACE_ATTRIBUTES, default=DEFAULT_REPLACE_ATTRIBUTES
            ): cv.boolean,
        },
        "async_update_variable",
    )

    config = hass.data.get(DOMAIN).get(config_entry.entry_id)
    unique_id = config_entry.entry_id
    # _LOGGER.debug(f"[async_setup_entry] config_entry: {config_entry.as_dict()}")
    # _LOGGER.debug(f"[async_setup_entry] config: {config}")
    # _LOGGER.debug(f"[async_setup_entry] unique_id: {unique_id}")

    async_add_entities([Variable(hass, config, config_entry, unique_id)])

    return True


class Variable(RestoreSensor):
    """Representation of a Sensor Variable."""

    def __init__(
        self,
        hass,
        config,
        config_entry,
        unique_id,
    ):
        """Initialize a Sensor Variable."""
        _LOGGER.debug(
            f"({config.get(CONF_NAME, config.get(CONF_VARIABLE_ID))}) [init] config: {config}"
        )
        self._hass = hass
        self._config = config
        self._config_entry = config_entry
        self._attr_has_entity_name = True
        self._variable_id = slugify(config.get(CONF_VARIABLE_ID).lower())
        self._attr_unique_id = unique_id
        if config.get(CONF_NAME) is not None:
            self._attr_name = config.get(CONF_NAME)
        else:
            self._attr_name = config.get(CONF_VARIABLE_ID)
        self._attr_icon = config.get(CONF_ICON)
        self._restore = config.get(CONF_RESTORE)
        self._force_update = config.get(CONF_FORCE_UPDATE)
        self._yaml_variable = config.get(CONF_YAML_VARIABLE)
        self._exclude_from_recorder = config.get(CONF_EXCLUDE_FROM_RECORDER)
        if (
            config.get(CONF_ATTRIBUTES) is not None
            and config.get(CONF_ATTRIBUTES)
            and isinstance(config.get(CONF_ATTRIBUTES), MutableMapping)
        ):
            self._attr_extra_state_attributes = self._update_attr_settings(
                config.get(CONF_ATTRIBUTES)
            )
        else:
            self._attr_extra_state_attributes = None
        self._value_type = config.get(CONF_VALUE_TYPE)
        self._attr_device_class = config.get(CONF_DEVICE_CLASS)
        self._attr_native_unit_of_measurement = config.get(CONF_UNIT_OF_MEASUREMENT)
        self._attr_state_class = config.get(CONF_STATE_CLASS)
        if config.get(CONF_VALUE) is None or (
            isinstance(config.get(CONF_VALUE), str)
            and config.get(CONF_VALUE).lower() in ["", "none", "unknown", "unavailable"]
        ):
            self._attr_native_value = None
        else:
            try:
                self._attr_native_value = value_to_type(
                    config.get(CONF_VALUE), self._value_type
                )
            except ValueError:
                self._attr_native_value = None
        self.entity_id = generate_entity_id(
            ENTITY_ID_FORMAT, self._variable_id, hass=self._hass
        )
        if self._exclude_from_recorder:
            self.disable_recorder()

    def disable_recorder(self):
        if RECORDER_INSTANCE in self._hass.data:
            ha_history_recorder = self._hass.data[RECORDER_INSTANCE]
            _LOGGER.info(f"({self._attr_name}) [disable_recorder] Disabling Recorder")
            if self.entity_id:
                try:
                    ha_history_recorder.entity_filter._exclude_e.add(self.entity_id)
                except AttributeError as e:
                    _LOGGER.warning(
                        f"({self._attr_name}) [disable_recorder] AttributeError trying to disable Recorder: {e}"
                    )
                else:
                    _LOGGER.debug(
                        f"({self._attr_name}) [disable_recorder] _exclude_e: {ha_history_recorder.entity_filter._exclude_e}"
                    )

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        if self._restore is True:
            _LOGGER.info(f"({self._attr_name}) Restoring after Reboot")
            sensor = await self.async_get_last_sensor_data()
            if sensor and hasattr(sensor, "native_value"):
                _LOGGER.debug(
                    f"({self._attr_name}) Restored sensor: {sensor.as_dict()}"
                )

                if sensor.native_value is None or (
                    isinstance(sensor.native_value, str)
                    and sensor.native_value.lower()
                    in [
                        "",
                        "none",
                        "unknown",
                        "unavailable",
                    ]
                ):
                    self._attr_native_value = None
                else:
                    try:
                        self._attr_native_value = value_to_type(
                            sensor.native_value, self._value_type
                        )
                    except ValueError:
                        self._attr_native_value = None
                # self._attr_native_unit_of_measurement = (
                #    sensor.native_unit_of_measurement
                # )
            state = await self.async_get_last_state()
            if state:
                _LOGGER.debug(f"({self._attr_name}) Restored state: {state.as_dict()}")
                if (
                    hasattr(state, "attributes")
                    and state.attributes
                    and isinstance(state.attributes, MutableMapping)
                ):
                    self._attr_extra_state_attributes = self._update_attr_settings(
                        state.attributes.copy()
                    )

                # Unsure how to deal with state vs native_value on restore.
                # Setting Restored state to override native_value for now.
                # self._state = state.state
                if (sensor is None and hasattr(state, "state")) or (
                    sensor
                    and hasattr(state, "state")
                    and state.state is not None
                    and hasattr(sensor, "native_value")
                    and sensor.native_value != state.state
                ):
                    if state.state is None or (
                        isinstance(state.state, str)
                        and state.state.lower()
                        in [
                            "",
                            "none",
                            "unknown",
                            "unavailable",
                        ]
                    ):
                        newval = None
                    else:
                        try:
                            newval = value_to_type(state.state, self._value_type)
                        except ValueError:
                            newval = None

                    _LOGGER.debug(f"({self._attr_name}) Updated state: |{newval}|")
                    if sensor.native_value is None or (
                        isinstance(sensor.native_value, str)
                        and sensor.native_value.lower()
                        in [
                            "",
                            "none",
                            "unknown",
                            "unavailable",
                        ]
                    ):
                        nat_val = None
                    else:
                        try:
                            nat_val = value_to_type(
                                sensor.native_value, self._value_type
                            )
                        except ValueError:
                            nat_val = None
                    if nat_val != newval:
                        _LOGGER.info(
                            f"({self._attr_name}) Restored values are different. "
                            f"native_value: {nat_val} | state: {newval}"
                        )
                        self._attr_native_value = newval

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""
        if RECORDER_INSTANCE in self._hass.data:
            ha_history_recorder = self._hass.data[RECORDER_INSTANCE]
            if self.entity_id:
                try:
                    ha_history_recorder.entity_filter._exclude_e.discard(self.entity_id)
                except AttributeError:
                    pass
                else:
                    _LOGGER.debug(
                        f"({self._attr_name}) Removing entity exclusion from recorder: {self.entity_id}"
                    )

    @property
    def should_poll(self):
        """If entity should be polled."""
        return False

    @property
    def force_update(self) -> bool:
        """Force update status of the entity."""
        return self._force_update

    def _update_attr_settings(self, new_attributes=None):
        if new_attributes is not None:
            if isinstance(new_attributes, MutableMapping):
                attributes = copy.deepcopy(new_attributes)
                for attrib, setting in VARIABLE_ATTR_SETTINGS.items():
                    if attrib in attributes.keys():
                        _LOGGER.debug(
                            f"({self._attr_name}) [update_attr_settings] attrib: {attrib} / setting: {setting} / value: {attributes.get(attrib)}"
                        )
                        setattr(self, setting, attributes.pop(attrib, None))
                return copy.deepcopy(attributes)
            else:
                _LOGGER.error(
                    f"({self._attr_name}) AttributeError: Attributes must be a dictionary: {new_attributes}"
                )
                return new_attributes
        else:
            return None

    # async def async_update_variable(self, value, attributes, replace_attributes=False) -> None:
    async def async_update_variable(self, **kwargs) -> None:
        """Update Sensor Variable."""

        updated_attributes = None

        replace_attributes = kwargs.get(ATTR_REPLACE_ATTRIBUTES, False)
        _LOGGER.debug(
            f"({self._attr_name}) [async_update_variable] Replace Attributes: {replace_attributes}"
        )

        if (
            not replace_attributes
            and hasattr(self, "_attr_extra_state_attributes")
            and self._attr_extra_state_attributes is not None
        ):
            updated_attributes = copy.deepcopy(self._attr_extra_state_attributes)

        attributes = kwargs.get(ATTR_ATTRIBUTES)
        if attributes is not None:
            if isinstance(attributes, MutableMapping):
                _LOGGER.debug(
                    f"({self._attr_name}) [async_update_variable] New Attributes: {attributes}"
                )
                extra_attributes = self._update_attr_settings(attributes)
                if updated_attributes is not None:
                    updated_attributes.update(extra_attributes)
                else:
                    updated_attributes = extra_attributes
            else:
                _LOGGER.error(
                    f"({self._attr_name}) AttributeError: Attributes must be a dictionary: {attributes}"
                )

        if ATTR_VALUE in kwargs:
            try:
                newval = value_to_type(kwargs.get(ATTR_VALUE), self._value_type)
            except ValueError:
                ERROR = f"The value entered is not compatible with the selected device_class: {self._attr_device_class}. Expected: {self._value_type}. Value: {kwargs.get(ATTR_VALUE)}"
                raise ValueError(ERROR)
                return
            else:
                _LOGGER.debug(
                    f"({self._attr_name}) [async_update_variable] New Value: {newval}"
                )
                self._attr_native_value = newval

        if updated_attributes is not None:
            self._attr_extra_state_attributes = copy.deepcopy(updated_attributes)
            _LOGGER.debug(
                f"({self._attr_name}) [async_update_variable] Final Attributes: {updated_attributes}"
            )
        else:
            self._attr_extra_state_attributes = None

        self.async_write_ha_state()
