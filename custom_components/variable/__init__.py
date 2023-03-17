"""Variable implementation for Home Assistant."""
import logging

from homeassistant.const import ATTR_ICON, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import ConfigType
from slugify import slugify
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

DOMAIN = "variable"
ENTITY_ID_FORMAT = DOMAIN + ".{}"

CONF_ATTRIBUTES = "attributes"
CONF_VALUE = "value"
CONF_RESTORE = "restore"
CONF_FORCE_UPDATE = "force_update"
CONF_DOMAIN = "domain"

ATTR_ENTITY = "entity"
ATTR_VARIABLE = "variable"
ATTR_VALUE = "value"
ATTR_ATTRIBUTES = "attributes"
ATTR_REPLACE_ATTRIBUTES = "replace_attributes"
ATTR_DOMAIN = "domain"

SERVICE_SET_ENTITY = "set_entity"
SERVICE_SET_VARIABLE = "set_variable"

SERVICE_SET_ENTITY_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY): cv.string,
        vol.Optional(ATTR_VALUE): cv.match_all,
        vol.Optional(ATTR_ATTRIBUTES): dict,
        vol.Optional(ATTR_REPLACE_ATTRIBUTES): cv.boolean,
    }
)
SERVICE_SET_VARIABLE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_VARIABLE): cv.string,
        vol.Optional(ATTR_VALUE): cv.match_all,
        vol.Optional(ATTR_ATTRIBUTES): dict,
        vol.Optional(ATTR_REPLACE_ATTRIBUTES): cv.boolean,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                cv.slug: vol.Any(
                    {
                        vol.Optional(CONF_NAME): cv.string,
                        vol.Optional(CONF_VALUE): cv.match_all,
                        vol.Optional(CONF_ATTRIBUTES): dict,
                        vol.Optional(CONF_RESTORE): cv.boolean,
                        vol.Optional(CONF_FORCE_UPDATE): cv.boolean,
                        vol.Optional(ATTR_DOMAIN): cv.string,
                    },
                    None,
                )
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def get_entity_id_format(domain: str) -> str:
    """Get the entity id format."""
    return domain + ".{}"


async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up variables."""
    component = EntityComponent(_LOGGER, DOMAIN, hass)

    entities = []

    for variable_id, variable_config in config[DOMAIN].items():
        if not variable_config:
            variable_config = {}

        name = variable_config.get(CONF_NAME)
        value = variable_config.get(CONF_VALUE)
        attributes = variable_config.get(CONF_ATTRIBUTES)
        restore = variable_config.get(CONF_RESTORE, False)
        force_update = variable_config.get(CONF_FORCE_UPDATE, False)
        domain = variable_config.get(CONF_DOMAIN, DOMAIN)

        entities.append(
            Variable(
                variable_id, name, value, attributes, restore, force_update, domain
            )
        )

    async def async_set_variable_service(call):
        """Handle calls to the set_variable service."""
        entity_id = ENTITY_ID_FORMAT.format(call.data.get(ATTR_VARIABLE))
        entity = component.get_entity(entity_id)

        if entity:
            await entity.async_set_variable(
                call.data.get(ATTR_VALUE),
                call.data.get(ATTR_ATTRIBUTES),
                call.data.get(ATTR_REPLACE_ATTRIBUTES, False),
            )
        else:
            _LOGGER.warning("Failed to set unknown variable: %s", entity_id)

    async def async_set_entity_service(call):
        """Handle calls to the set_entity service."""

        entity_id: str = call.data.get(ATTR_ENTITY)
        state_value = call.data.get(ATTR_VALUE)
        attributes = call.data.get(ATTR_ATTRIBUTES, {})
        replace_attributes = call.data.get(ATTR_REPLACE_ATTRIBUTES, False)

        if replace_attributes:
            updated_attributes = attributes
        else:
            cur_state = hass.states.get(entity_id)
            if cur_state is None or cur_state.attributes is None:
                updated_attributes = attributes
            else:
                updated_attributes = dict(cur_state.attributes)
                updated_attributes.update(attributes)

        hass.states.async_set(entity_id, state_value, updated_attributes)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_VARIABLE,
        async_set_variable_service,
        schema=SERVICE_SET_VARIABLE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_ENTITY,
        async_set_entity_service,
        schema=SERVICE_SET_ENTITY_SCHEMA,
    )

    await component.async_add_entities(entities)
    return True


class Variable(RestoreEntity):
    """Representation of a variable."""

    def __init__(
        self,
        variable_id,
        name,
        value,
        attributes,
        restore,
        force_update,
        domain
    ):
        """Initialize a variable."""

        self.entity_id = get_entity_id_format(domain).format(variable_id)
        self._name = name
        self._value = value
        self._attributes = attributes
        self._restore = restore
        self._force_update = force_update
        self._attr_unique_id = slugify(DOMAIN + self.entity_id)

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        if self._restore is True:
            # If variable state have been saved.
            state = await self.async_get_last_state()
            if state:
                # restore state
                self._value = state.state
                # restore value
                self._attributes = state.attributes

    @property
    def should_poll(self):
        """If entity should be polled."""
        return False

    @property
    def name(self):
        """Return the name of the variable."""
        return self._name

    @property
    def icon(self):
        """Return the icon to be used for this entity."""
        if self._attributes is not None:
            return self._attributes.get(ATTR_ICON)
        return None

    @property
    def state(self):
        """Return the state of the component."""
        return self._value

    @property
    def state_attributes(self):
        """Return the attributes of the variable."""
        return self._attributes

    @property
    def force_update(self) -> bool:
        """Force update of the entity."""
        return self._force_update

    async def async_set_variable(
        self,
        value,
        attributes,
        replace_attributes,
    ):
        """Update variable."""
        updated_attributes = None
        updated_value = None

        if not replace_attributes and self._attributes is not None:
            updated_attributes = dict(self._attributes)

        if attributes is not None:
            if updated_attributes is not None:
                updated_attributes.update(attributes)
            else:
                updated_attributes = attributes

        if value is not None:
            updated_value = value

        self._attributes = updated_attributes

        if updated_value is not None:
            self._value = updated_value

        await self.async_update_ha_state()
