# Variables+History
### aka. `variable`

<picture>
  <img alt="Variable Logo" src="https://github.com/Wibias/hass-variables/raw/master/logo/icon.png">
</picture>

A Home Assistant Integration to declare and set/update variables.

Forked and updated from initial integration developed by [rogro82](https://github.com/rogro82)

## Upgrading from v2 to v3
**Existing variables will remain as yaml variables but instead of starting with `variable.`, they will now start with `sensor.` If you would like to manage the variable using the UI configuration, you will need to delete the entity from your yaml and recreate it in the UI.**

## Installation

### HACS *(recommended)*
1. Ensure that [HACS](https://hacs.xyz/) is installed
1. [Click Here](https://my.home-assistant.io/redirect/hacs_repository/?owner=Wibias&repository=hass-variables) to directly open `Variables+History` in HACS **or**<br/>
  a. Navigate to HACS<br/>
  b. Click `+ Explore & Download Repositories`<br/>
  c. Find the `Variables+History` integration <br/>
1. Click `Download`
1. Restart Home Assistant
1. See [Configuration](#configuration) below

<details>
<summary><h3>Manual</h3></summary>

You probably **do not** want to do this! Use the HACS method above unless you know what you are doing and have a good reason as to why you are installing manually

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`)
1. If you do not have a `custom_components` directory there, you need to create it
1. In the `custom_components` directory create a new folder called `variable`
1. Download _all_ the files from the `custom_components/variable/` directory in this repository
1. Place the files you downloaded in the new directory you created
1. Restart Home Assistant
1. See [Configuration](#configuration) below
</details>

## Preferred Configuration
1. [Click Here](https://my.home-assistant.io/redirect/config_flow_start/?domain=variable) to directly add a `Variables+History` sensor **or**<br/>
  a. In Home Assistant, go to Settings -> [Integrations](https://my.home-assistant.io/redirect/integrations/)<br/>
  b. Click `+ Add Integrations` and select `Variables+History`<br/>
1. Add your configuration ([see Configuration Options below](#configuration-options))
1. Click `Submit`
* Repeat as needed to create additional `Variables+History` sensors
* Options can be changed for existing `Variables+History` sensors in Home Assistant Integrations by selecting `Configure` under the desired `Variables+History` sensor.

## Configuration Options

### First choose the `variable` type.

<details>
<summary><h3>Sensor</h3></summary>

Name | Required | Default | Description |
-- | -- | -- | --
`Variable ID` | `Yes` | | The desired id of the new sensor (ex. `test_variable` would create an entity_id of `sensor.test_variable`)
`Name` | `No` | | Friendly name of the variable sensor
`Icon` | `No` | `mdi:variable` | Icon of the Variable
`Initial Value` | `No` | | Initial value/state of the variable. If `Restore on Restart` is `False`, the variable will reset to this value on every restart
`Initial Attributes` | `No` | | Initial attributes of the variable. If `Restore on Restart` is `False`, the variable will reset to this value on every restart
`Restore on Restart` | `No` | `True` | If `True` will restore previous value on restart. If `False`, will reset to `Initial Value` and `Initial Attributes` on restart
`Force Update` | `No` | `False` | Variable's `last_updated` time will change with any service calls to update the variable even if the value does not change
`Exclude from Recorder` | `No` | `False` | For Variables with large attributes (>16 kB), enable this to prevent Recorder Errors.

</details>

<details>
<summary><h3>Binary Sensor</h3></summary>

Name | Required | Default | Description |
-- | -- | -- | --
`Variable ID` | `Yes` | | The desired id of the new binary sensor (ex. `test_variable` would create an entity_id of `binary_sensor.test_variable`)
`Name` | `No` | | Friendly name of the variable binary sensor
`Icon` | `No` | `mdi:variable` | Icon of the Variable
`Initial Value` | `No` | `False` | Initial `True`/`False` value/state of the variable. If `Restore on Restart` is `False`, the variable will reset to this value on every restart
`Initial Attributes` | `No` | | Initial attributes of the variable. If `Restore on Restart` is `False`, the variable will reset to this value on every restart
`Restore on Restart` | `No` | `True` | If `True` will restore previous value on restart. If `False`, will reset to `Initial Value` and `Initial Attributes` on restart
`Force Update` | `No` | `False` | Variable's `last_updated` time will change with any service calls to update the variable even if the value does not change
`Exclude from Recorder` | `No` | `False` | For Variables with large attributes (>16 kB), enable this to prevent Recorder Errors.

</details>

<details>
<summary><h2>Alternate YAML Configuration</h2></summary>

**Variables created via YAML will all start with `sensor.` and cannot be edited in the UI.**

_You can have a combination of Variables created via the UI and via YAML._

Add the component `variable` to your configuration and declare the variables you want.

Name | yaml | Required | Default | Description |
-- | -- | -- | -- | --
Variable ID | `<key>:` | `Yes` | | The desired id of the new sensor (ex. `test_variable` would create an entity_id of `sensor.test_variable`)
Name | `name` | `No` | | Friendly name of the variable sensor  
Initial Value | `value` | `No` | | Initial value/state of the variable. If `Restore on Restart` is `False`, the variable will reset to this value on every restart
Initial Attributes | `attributes` | `No` | | Initial attributes of the variable. If `Restore on Restart` is `False`, the variable will reset to this value on every restart
Restore on Restart | `restore` | `No` | `True` | If `True` will restore previous value on restart. If `False`, will reset to `Initial Value` and `Initial Attributes` on restart
Force Update | `force_update` | `No` | `False` | Variable's `last_updated` time will change with any service calls to update the variable even if the value does not change
Exclude from Recorder | `exclude_from_recorder` | `No` | `False` | For Variables with large attributes (>16 kB), set to `True` to prevent Recorder Errors.  

#### Example:

```yaml
variable:
  countdown_timer:
    value: 30
    attributes:
      friendly_name: 'Countdown'
      icon: mdi:alarm
  countdown_trigger:
    name: Countdown
    value: False
  light_scene:
    value: 'normal'
    attributes:
      previous: ''
    restore: true
  current_power_usage:
    force_update: true

  daily_download:
    value: 0
    restore: true
    attributes:
      state_class: measurement
      unit_of_measurement: GB
      icon: mdi:download
```

</details>

<details>
<summary><h2>Alternate YAML Configuration</h2></summary>

**Variables created via YAML will all start with `sensor.` and cannot be edited in the UI.**

_You can have a combination of Variables created via the UI and via YAML._

Add the component `variable` to your configuration and declare the variables you want.

Name | yaml | Required | Default | Description |
-- | -- | -- | -- | --
Variable ID | `<key>:` | `Yes` | | The desired id of the new sensor (ex. `test_variable` would create an entity_id of `sensor.test_variable`)
Name | `name` | `No` | | Friendly name of the variable sensor  
Initial Value | `value` | `No` | | Initial value/state of the variable. If `Restore on Restart` is `False`, the variable will reset to this value on every restart
Initial Attributes | `attributes` | `No` | | Initial attributes of the variable. If `Restore on Restart` is `False`, the variable will reset to this value on every restart
Restore on Restart | `restore` | `No` | `True` | If `True` will restore previous value on restart. If `False`, will reset to `Initial Value` and `Initial Attributes` on restart
Force Update | `force_update` | `No` | `False` | Variable's `last_updated` time will change with any service calls to update the variable even if the value does not change

#### Example:

```yaml
variable:
  countdown_timer:
    value: 30
    attributes:
      friendly_name: 'Countdown'
      icon: mdi:alarm
  countdown_trigger:
    name: Countdown
    value: False
  light_scene:
    value: 'normal'
    attributes:
      previous: ''
    restore: true
  current_power_usage:
    force_update: true

  daily_download:
    value: 0
    restore: true
    attributes:
      state_class: measurement
      unit_of_measurement: GB
      icon: mdi:download
```

</details>

## Services

There are instructions and selectors when the service is called from the Developer Tools or within a Script or Automation.

### `variable.update_sensor`

Used to update the value or attributes of a Sensor Variable

Name | Key | Required | Default | Description |
-- | -- | -- | -- | -- |
`Targets` | `target:`<br />&nbsp;&nbsp;`entity_id:`  | `Yes` | | The entity_ids of one or more sensor variables to update (ex. `sensor.test_variable`)
`New Value` | `value` | `No` | | Value/state to change the variable to
`New Attributes` | `attributes` | `No` | | What to update the attributes to
`Replace Attributes` | `replace_attributes` | `No` | `False` | Replace or merge current attributes (`False` = merge)


### `variable.update_binary_sensor`

Used to update the value or attributes of a Binary Sensor Variable

Name | Key | Required | Default | Description |
-- | -- | -- | -- | -- |
`Targets` | `target:`<br />&nbsp;&nbsp;`entity_id:`  | `Yes` | | The entity_ids of one or more binary sensor variables to update (ex. `binary_sensor.test_variable`)
`New Value` | `value` | `No` | | Value/state to change the variable to
`New Attributes` | `attributes` | `No` | | What to update the attributes to
`Replace Attributes` | `replace_attributes` | `No` | `False` | Replace or merge current attributes (`False` = merge)

<details>
<summary><h2>Legacy Services</h2></summary>

#### These will only work for Sensor Variables
_These services are from the previous version of the integration and are being kept for pre-existing automations and scripts. In general, the new `variable.update_` services above should be used going forward._

Both services are similar and used to update the value or attributes of a Sensor Variable. `variable.set_variable` uses just the `variable_id` and `variable.set_entity` uses the full `entity_id`. There are instructions and selectors when the service is called from the Developer Tools or within a Script or Automation.

### `variable.set_variable`

Name | Key | Required | Default | Description |
-- | -- | -- | -- | -- |
`Variable ID` | `variable`  | `Yes` | | The id of the sensor variable to update (ex. `test_variable` for a sensor variable of `sensor.test_variable`)
`Value` | `value` | `No` | | Value/state to change the variable to
`Attributes` | `attributes` | `No` | | What to update the attributes to
`Replace Attributes` | `replace_attributes` | `No` | `False` | Replace or merge current attributes (`False` = merge)

### `variable.set_entity`

Name | Key | Required | Default | Description |
-- | -- | -- | -- | -- |
`Entity ID` | `entity`  | `Yes` | | The entity_id of the sensor variable to update (ex. `sensor.test_variable`)
`Value` | `value` | `No` | | Value/state to change the variable to
`Attributes` | `attributes` | `No` | | What to update the attributes to
`Replace Attributes` | `replace_attributes` | `No` | `False` | Replace or merge current attributes (`False` = merge)

</details>

## Example service calls

```yaml
action:
  - service: variable.update_sensor
    data:
      value: 30
    target:
      entity_id: sensor.test_timer
```
```yaml
action:
  - service: variable.update_sensor
    data:
      value: >-
        {{trigger.to_state.name|replace('Motion Sensor','')}}
      attributes:
        history_1: "{{states('sensor.last_motion')}}"
        history_2: "{{state_attr('sensor.last_motion','history_1')}}"
        history_3: "{{state_attr('sensor.last_motion','history_2')}}"
    target:
      entity_id: sensor.last_motion
```
```yaml
action:
  - service: variable.update_binary_sensor
    data:
      value: true
      replace_attributes: true
      attributes:
        country: USA
    target:
      entity_id: binary_sensor.test_binary_var
```

## Example timer automation

* Create a sensor variable with the Variable ID of `test_timer` and Initial Value of `0`

```yaml
script:
  schedule_test_timer:
    sequence:
      - service: variable.update_sensor
        data:
          value: 30
        target:
          entity_id: sensor.test_timer
      - service: automation.turn_on
        data:
          entity_id: automation.test_timer_countdown

automation:
  - alias: test_timer_countdown
    initial_state: 'off'
    trigger:
      - platform: time_pattern
        seconds: '/1'
    action:
      - service: variable.update_sensor
        data:
          value: >
            {{ [((states('sensor.test_timer') | int(default=0)) - 1), 0] | max }}
        target:
          entity_id: sensor.test_timer
  - alias: test_timer_trigger
    trigger:
      platform: state
      entity_id: sensor.test_timer
      to: '0'
    action:
      - service: automation.turn_off
        data:
          entity_id: automation.test_timer_countdown
```

## Examples

<details>
<summary><h3>Play and Save TTS Messages + Message History - Made by <a href="https://github.com/jazzyisj">jazzyisj</a></h3></summary>

#### https://github.com/jazzyisj/save-tts-messages

This is more or less an answering machine (remember those?) for your TTS messages. When you play a TTS message that you want saved under certain conditions (ie. nobody is home), you will call the script Play or Save TTS Message script.play_or_save_message instead of calling your tts service (or Alexa notify) directly. The script will decide whether to play the message immediately, or save it based on the conditions you specify. If a saved tts message is repeated another message is not saved, only the timestamp is updated to the most recent instance.

Messages are played back using the Play Saved TTS Messages script script.play_saved_tts_messages. Set an appropriate trigger (for example when you arrive home) in the automation Play Saved Messages automation.play_saved_messages automation to call this script automatically.

Saved messages will survive restarts.

BONUS - OPTIONAL TTS MESSAGE HISTORY

You can find the full documentation on how to do this and adjust this to your needs in [here](https://github.com/Wibias/hass-variables/tree/master/examples/save-tts-message/tts.md).
</details>

#### More examples can be found in the [examples](https://github.com/Wibias/hass-variables/tree/master/examples) folder.
