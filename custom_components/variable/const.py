from homeassistant.const import Platform

DOMAIN = "variable"

PLATFORMS: list[str] = [Platform.SENSOR, Platform.BINARY_SENSOR]

# Defaults
DEFAULT_FORCE_UPDATE = False
DEFAULT_ICON = "mdi:variable"
DEFAULT_REPLACE_ATTRIBUTES = False
DEFAULT_RESTORE = True

CONF_ATTRIBUTES = "attributes"
CONF_ENTITY_PLATFORM = "entity_platform"
CONF_FORCE_UPDATE = "force_update"
CONF_RESTORE = "restore"
CONF_VALUE = "value"
CONF_VARIABLE_ID = "variable_id"

ATTR_ATTRIBUTES = "attributes"
ATTR_ENTITY = "entity"
ATTR_REPLACE_ATTRIBUTES = "replace_attributes"
ATTR_VALUE = "value"
ATTR_VARIABLE = "variable"
