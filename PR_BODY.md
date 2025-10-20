Short summary

- Silence type-checker override / cached_property mismatches with narrow `# type: ignore[override]` on the affected properties.
- Replace an `assert` in `custom_components/variable/sensor.py` with a runtime-safe check to avoid Bandit B101.

- Remove orphaned YAML-imported variables: detect variables removed from YAML and delete their corresponding config entries.
- Cleanup entity registry entries when a config entry unloads to avoid orphaned entities (entities without unique_id) showing in the Entities list.

Files changed

- `custom_components/variable/device_tracker.py`
- `custom_components/variable/binary_sensor.py`
- `custom_components/variable/sensor.py`
- `custom_components/variable/__init__.py`
- `custom_components/variable/manifest.json`
 - `custom_components/variable/config_flow.py`

Why

Home Assistant stubs declare some properties as `cached_property` / `final`. These changes avoid CI failures while preserving runtime behavior.

Config flow & options fixes

- Normalize and guard `user_input` in options flow steps so `.get()`/`.update()` are safe for type checkers.
- Make iso4217 an optional import and guard iteration over currencies.
- Replace direct references to `sensor.DEVICE_CLASS_UNITS` with a safe getattr fallback.
- Coerce `description_placeholders` values to `str()` so they match Home Assistant's expected `Mapping[str, str]`.
- Initialize `entity_id`/`state` locals before use and guard `state` accesses.
- Add an AwesomeVersion/HAVERSION guard so older HA versions keep `config_entry` on the OptionsFlow handler (Closes #140).

Notes

- No functionality removed. All changes are defensive typing/guard fixes.
 - No functionality removed. All changes are defensive typing/guard fixes.

Closes: https://github.com/enkama/hass-variables/issues/140
Related issue: https://github.com/enkama/hass-variables/issues/141
