import logging

from homeassistant.components.sensor import PLATFORM_SCHEMA, RestoreSensor
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
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
    CONF_FORCE_UPDATE,
    CONF_RESTORE,
    CONF_VALUE,
    CONF_VARIABLE_ID,
    DEFAULT_FORCE_UPDATE,
    DEFAULT_ICON,
    DEFAULT_REPLACE_ATTRIBUTES,
    DEFAULT_RESTORE,
    DOMAIN,
    SENSOR_DEVICE_CLASS_SELECT_LIST,
)

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
    }
)

SERVICE_UPDATE_VARIABLE = "update_" + PLATFORM


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
        if config.get(CONF_VALUE) is not None:
            self._attr_native_value = config.get(CONF_VALUE)
        if config.get(CONF_ATTRIBUTES) is not None and config.get(CONF_ATTRIBUTES):
            self._attr_extra_state_attributes = config.get(CONF_ATTRIBUTES)
        self._restore = config.get(CONF_RESTORE)
        self._force_update = config.get(CONF_FORCE_UPDATE)
        self.entity_id = generate_entity_id(
            ENTITY_ID_FORMAT, self._variable_id, hass=self._hass
        )
        # _LOGGER.debug(f"[init] name: {self._attr_name}")
        # _LOGGER.debug(f"[init] variable_id: {self._variable_id}")
        # _LOGGER.debug(f"[init] entity_id: {self.entity_id}")
        # _LOGGER.debug(f"[init] unique_id: {self._attr_unique_id}")
        # _LOGGER.debug(f"[init] icon: {self._attr_icon}")
        # _LOGGER.debug(f"[init] value: {self._attr_is_on}")
        # _LOGGER.debug(f"[init] attributes: {self._attr_extra_state_attributes}")
        # _LOGGER.debug(f"[init] restore: {self._restore}")
        # _LOGGER.debug(f"[init] force_update: {self._force_update}")

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        if self._restore is True:
            _LOGGER.info(f"({self._attr_name}) Restoring after Reboot")
            sensor = await self.async_get_last_sensor_data()
            if sensor:
                _LOGGER.debug(
                    f"({self._attr_name}) Restored sensor: {sensor.as_dict()}"
                )
                self._attr_native_value = sensor.native_value
            state = await self.async_get_last_state()
            if state:
                _LOGGER.debug(f"({self._attr_name}) Restored state: {state.as_dict()}")
                self._attr_extra_state_attributes = state.attributes

                # Unsure how to deal with state vs native_value on restore.
                # Setting Restored state to override native_value for now.
                # self._state = state.state
                if (sensor is None or (
                    sensor and state.state is not None
                    and state.state.lower() != "none"
                    and sensor.native_value != state.state
                )):
                    _LOGGER.info(
                        f"({self._attr_name}) Restored values are different. "
                        f"native_value: {sensor.native_value} | state: {state.state}"
                    )
                    self._attr_native_value = state.state

    @property
    def should_poll(self):
        """If entity should be polled."""
        return False

    @property
    def force_update(self) -> bool:
        """Force update status of the entity."""
        return self._force_update

    async def async_update_variable(
        self,
        value=None,
        attributes=None,
        replace_attributes=False,
    ) -> None:
        """Update Sensor Variable."""

        updated_attributes = None
        updated_value = None

        if not replace_attributes and self._attr_extra_state_attributes is not None:
            updated_attributes = dict(self._attr_extra_state_attributes)

        if attributes is not None:
            if updated_attributes is not None:
                updated_attributes.update(attributes)
            else:
                updated_attributes = attributes

        if value is not None:
            updated_value = value

        self._attr_extra_state_attributes = updated_attributes

        if updated_value is not None:
            self._attr_native_value = updated_value

        await self.async_update_ha_state()
