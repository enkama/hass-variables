from homeassistant.const import Platform

DOMAIN = "variable"

PLATFORMS: list[str] = [Platform.SENSOR, Platform.BINARY_SENSOR]

# Defaults
DEFAULT_FORCE_UPDATE = False
DEFAULT_ICON = "mdi:variable"
DEFAULT_REPLACE_ATTRIBUTES = False
DEFAULT_RESTORE = True
DEFAULT_EXCLUDE_FROM_RECORDER = False

CONF_ATTRIBUTES = "attributes"
CONF_ENTITY_PLATFORM = "entity_platform"
CONF_FORCE_UPDATE = "force_update"
CONF_RESTORE = "restore"
CONF_VALUE = "value"
CONF_VARIABLE_ID = "variable_id"
CONF_YAML_VARIABLE = "yaml_variable"
CONF_EXCLUDE_FROM_RECORDER = "exclude_from_recorder"

ATTR_ATTRIBUTES = "attributes"
ATTR_ENTITY = "entity"
ATTR_REPLACE_ATTRIBUTES = "replace_attributes"
ATTR_VALUE = "value"
ATTR_VARIABLE = "variable"
