"""Variable implementation for Home Assistant."""
import json
import logging

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_FRIENDLY_NAME, CONF_ICON, CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_registry as er
from homeassistant.helpers.typing import ConfigType
import voluptuous as vol

from .const import (
    ATTR_ATTRIBUTES,
    ATTR_ENTITY,
    ATTR_REPLACE_ATTRIBUTES,
    ATTR_VALUE,
    ATTR_VARIABLE,
    CONF_ATTRIBUTES,
    CONF_ENTITY_PLATFORM,
    CONF_FORCE_UPDATE,
    CONF_RESTORE,
    CONF_VALUE,
    CONF_VARIABLE_ID,
    DOMAIN,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)

try:
    use_issue_reg = True
    from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue
except Exception as e:
    _LOGGER.debug(
        "Unknown Exception trying to import issue_registry. Is HA version <2022.9?: "
        + str(e)
    )
    use_issue_reg = False

SERVICE_SET_VARIABLE_LEGACY = "set_variable"
SERVICE_SET_ENTITY_LEGACY = "set_entity"

SERVICE_SET_VARIABLE_LEGACY_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_VARIABLE): cv.string,
        vol.Optional(ATTR_VALUE): cv.match_all,
        vol.Optional(ATTR_ATTRIBUTES): dict,
        vol.Optional(ATTR_REPLACE_ATTRIBUTES): cv.boolean,
    }
)

SERVICE_SET_ENTITY_LEGACY_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY): cv.string,
        vol.Optional(ATTR_VALUE): cv.match_all,
        vol.Optional(ATTR_ATTRIBUTES): dict,
        vol.Optional(ATTR_REPLACE_ATTRIBUTES): cv.boolean,
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the Variable services."""
    # _LOGGER.debug("Starting async_setup")
    # _LOGGER.debug("[async_setup] config: " + str(config))

    async def async_set_variable_legacy_service(call):
        """Handle calls to the set_variable legacy service."""

        ENTITY_ID_FORMAT = Platform.SENSOR + ".{}"
        _LOGGER.debug("Starting async_set_variable_legacy_service")
        _LOGGER.debug("call: " + str(call))

        entity_id = ENTITY_ID_FORMAT.format(call.data.get(ATTR_VARIABLE))
        _LOGGER.debug("entity_id: " + str(entity_id))
        entity_registry = er.async_get(hass)
        entity = entity_registry.async_get(entity_id)

        _LOGGER.debug("entity: " + str(entity))
        _LOGGER.debug("entity platform: " + str(entity.platform))
        if entity and entity.platform == DOMAIN:
            _LOGGER.debug("Updating variable")
            pre_state = hass.states.get(entity_id=entity_id)
            pre_attr = hass.states.get(entity_id=entity_id).attributes
            _LOGGER.debug("Previous state: " + str(pre_state.as_dict()))
            _LOGGER.debug("Previous attr: " + str(pre_attr))
            if not call.data.get(ATTR_REPLACE_ATTRIBUTES, False):
                if call.data.get(ATTR_ATTRIBUTES):
                    new_attr = pre_attr | call.data.get(ATTR_ATTRIBUTES)
                else:
                    new_attr = pre_attr
            else:
                new_attr = call.data.get(ATTR_ATTRIBUTES)
            _LOGGER.debug("Updated attr: " + str(new_attr))
            hass.states.async_set(
                entity_id=entity_id,
                new_state=call.data.get(ATTR_VALUE),
                attributes=new_attr,
            )
            _LOGGER.debug(
                "Post state: " + str(hass.states.get(entity_id=entity_id).as_dict())
            )
        else:
            _LOGGER.warning("Failed to set. Unknown Variable: %s", entity_id)

    async def async_set_entity_legacy_service(call):
        """Handle calls to the set_entity legacy service."""

        _LOGGER.debug("Starting async_set_entity_legacy_service")
        _LOGGER.debug("call: " + str(call))

        entity_id: str = call.data.get(ATTR_ENTITY)
        _LOGGER.debug("entity_id: " + str(entity_id))
        entity_registry = er.async_get(hass)
        entity = entity_registry.async_get(entity_id)

        _LOGGER.debug("entity: " + str(entity))
        _LOGGER.debug("entity platform: " + str(entity.platform))
        if entity and entity.platform == DOMAIN:
            _LOGGER.debug("Updating variable")
            pre_state = hass.states.get(entity_id=entity_id)
            pre_attr = hass.states.get(entity_id=entity_id).attributes
            _LOGGER.debug("Previous state: " + str(pre_state.as_dict()))
            _LOGGER.debug("Previous attr: " + str(pre_attr))
            if not call.data.get(ATTR_REPLACE_ATTRIBUTES, False):
                if call.data.get(ATTR_ATTRIBUTES):
                    new_attr = pre_attr | call.data.get(ATTR_ATTRIBUTES)
                else:
                    new_attr = pre_attr
            else:
                new_attr = call.data.get(ATTR_ATTRIBUTES)
            _LOGGER.debug("Updated attr: " + str(new_attr))
            hass.states.async_set(
                entity_id=entity_id,
                new_state=call.data.get(ATTR_VALUE),
                attributes=new_attr,
            )
            _LOGGER.debug(
                "Post state: " + str(hass.states.get(entity_id=entity_id).as_dict())
            )
        else:
            _LOGGER.warning("Failed to set. Unknown Variable: %s", entity_id)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_VARIABLE_LEGACY,
        async_set_variable_legacy_service,
        schema=SERVICE_SET_VARIABLE_LEGACY_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_ENTITY_LEGACY,
        async_set_entity_legacy_service,
        schema=SERVICE_SET_ENTITY_LEGACY_SCHEMA,
    )

    # _LOGGER.debug("*******************************************************************")
    variables = json.loads(json.dumps(config.get(DOMAIN, {})))
    # _LOGGER.debug("[async_setup] variables: " + str(variables))

    if variables and use_issue_reg:
        async_create_issue(
            hass,
            DOMAIN,
            "restart_required_variable",
            is_fixable=True,
            severity=IssueSeverity.WARNING,
            translation_key="restart_required_variable",
        )

    for var, var_fields in variables.items():
        if var is not None and var not in {
            entry.data.get(CONF_VARIABLE_ID)
            for entry in hass.config_entries.async_entries(DOMAIN)
        }:
            _LOGGER.warning("[YAML Import] New YAML sensor, importing: " + str(var))
            _LOGGER.debug("[YAML Import] var_fields: " + str(var_fields))

            attr = var_fields.get(CONF_ATTRIBUTES, {})
            icon = attr.pop(CONF_ICON, None)
            name = var_fields.get(CONF_NAME, attr.pop(CONF_FRIENDLY_NAME, None))
            attr.pop(CONF_FRIENDLY_NAME, None)

            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN,
                    context={"source": SOURCE_IMPORT},
                    data={
                        CONF_ENTITY_PLATFORM: Platform.SENSOR,
                        CONF_VARIABLE_ID: var,
                        CONF_NAME: name,
                        CONF_VALUE: var_fields.get(CONF_VALUE),
                        CONF_RESTORE: var_fields.get(CONF_RESTORE),
                        CONF_FORCE_UPDATE: var_fields.get(CONF_FORCE_UPDATE),
                        CONF_ATTRIBUTES: attr,
                        CONF_ICON: icon,
                    },
                )
            )
        else:
            _LOGGER.info("[YAML Import] Already Imported: " + str(var))

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""

    entry.options = {}
    _LOGGER.debug("[init async_setup_entry] entry: " + str(entry.data))
    hass.data.setdefault(DOMAIN, {})
    hass_data = dict(entry.data)
    hass.data[DOMAIN][entry.entry_id] = hass_data
    _LOGGER.debug(
        "[init async_setup_entry] entity_platform: "
        + str(hass_data.get(CONF_ENTITY_PLATFORM))
    )
    if hass_data.get(CONF_ENTITY_PLATFORM) in PLATFORMS:
        await hass.config_entries.async_forward_entry_setups(
            entry, [hass_data.get(CONF_ENTITY_PLATFORM)]
        )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    _LOGGER.info("Unloading: " + str(entry.data))
    hass_data = dict(entry.data)
    if hass_data.get(CONF_ENTITY_PLATFORM) in PLATFORMS:
        unload_ok = await hass.config_entries.async_unload_platforms(
            entry, [hass_data.get(CONF_ENTITY_PLATFORM)]
        )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


# async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
#    """Handle options update."""
#
#    _LOGGER.debug("[init update_listener] entry: " + str(entry.as_dict()))
#    await hass.config_entries.async_reload(entry.entry_id)
