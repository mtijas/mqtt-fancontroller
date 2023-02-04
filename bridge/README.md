# The MQTT Fan Controller Bridge

## Description

The bridge acts as a middleman between a MQTT broker and the Arduino-based
PID fan controller (connected via a serial port [USB] to the bridge). The bridge subscribes
to a command topic described in the config, and forwards the commands received in
that topic to the Controller via a serial port. The responses from the
Controller will be forwarded to the topics also described in the config.

## Installation

There is currently no easy way to install the package since it's still
in early development phase (well, pip might offer something, but YMMV).

## Configuration

### The config file

The Bridge expects to find a config file in `$XDG_CONFIG_HOME/fancontrolbridge/config.yaml`.
This may be overridden by specifying a config file when starting the Bridge with
the flag `-c` (example: `fancontrolbridge -c ./config.yaml`).

Example of a full config file:

```yaml
modules:
  - type: mqttmessenger
    config:
      publish_events:
        channel_1_status: fancontrolbridge/test/ch1/status
        channel_2_status: fancontrolbridge/test/ch2/status
        channel_1_settings: fancontrolbridge/test/ch1/settings
        channel_2_settings: fancontrolbridge/test/ch2/settings
        controller_command_results: fancontrolbridge/command-results
      subscribe_topics:
        - fancontrolbridge/commands
      host: <mqtt_bridge_host>
  - type: fancontrollercommunicator
    config:
      port: /dev/ttyACM0
      bauds: 9600
      command_topic: fancontrolbridge/commands
```

### The MQTTMessenger config

#### `publish_events` and `subscribe_topics`

The configuration file allows setting command topic which the Bridge
will then listen to for the commands, and the topics to which the responses
from the Controller should be forwarded to.

Command topic config example:

```yaml
subscribe_topics:
  - fancontrolbridge/commands
```

Response publish topics config example:

```yaml
publish_events:
  channel_1_status: fancontrolbridge/test/ch1/status
  channel_2_status: fancontrolbridge/test/ch2/status
  channel_1_settings: fancontrolbridge/test/ch1/settings
  channel_2_settings: fancontrolbridge/test/ch2/settings
  controller_command_results: fancontrolbridge/command-results
```

The commands received from the commands topics will be evaluated and sent
to the Controller if they are formed correctly. Evaluation results of all commands
and the results of sending the commands to the Controller commands will be forwarded
to the `controller_command_results` topic.

The responses from the Controller for `GET` commands will be forwarded to the topics
`channel_<number>_status` (for status report commands) and `channel_<number>_settings`
(for getting the current settings).

**To recap:**

- There will be a message in `controller_command_results` for *every* command
received from the command topics.
  - Listen to this to determine if any command got successfully forwarded.

- Sending `GET_STATUS` command results in a response to `channel_<number>_status`
topic containing current status (temps, rpm and output) of one channel on the Controller.

- Sending `GET_SETTINGS` command results in a response to `channel_<number>_settings`
topic containing current settings (mode and PID parameters) of one channel on the Controller.

#### Setting the MQTT broker host, username and password

The location of your MQTT broker must be set in `host: <mqtt_bridge_host>`.

If your MQTT broker requires username and password to be provided, you may
export them as environment variables inside the container before starting
the application (in Linux):

```sh
export FANCONTROLBRIDGE_MQTTMESSENGER__USERNAME=username
export FANCONTROLBRIDGE_MQTTMESSENGER__PASSWORD=password
```

You may also provide these via a `.env` file as is expected in the `docker-compose.yaml` file.

### The FanControllerCommunicator config

#### port

The port in which the Controller is connected. Sometimes `/dev/ttyACM0`.

#### bauds

Communication speed of the Controller. Usually `9600`.

#### command_topic

The MQTT topic on which the commands get delivered to the Bridge. **Should
match** one of the `subscribe_topics` on MQTTMessenger configuration. This allows
us to develop additional MQTT-listening functionality which are necessarily
not Controller Command topics.

In the example config: `command_topic: fancontrolbridge/commands`.


## Running

*TBA*

## Commands

The Bridge expects commands to be sent as JSON objects.

For *setting* a parameter of the Controller, the command object should
contain *command*, *channel* and *value*:

```
{"command": <command_name_string>, "channel": <channel_id>, "value": <value_to_set>}
```

And for getting status and settings reports from the Controller, leave the
value out of the command JSON:

```
{"command": <command_name_string>, "channel": <channel_id>}
```

The command names are fixed, and the channel may currently be 1 or 2.

### SET_TARGET

The Command `SET_TARGET` sets a new target temperature for a channel.
The target temperature will be **cut** to one decimal (Example: 23.56 -> 23.5).
Use a period as decimal separator.

Example of setting target temperature to 42.5 C on channel 1:

```json
{"command": "SET_TARGET", "channel": 1, "value": 42.5}
```

### SET_KP

The command `SET_KP` sets the P control term of the PID
controller for a channel. The value will be **cut** to two decimals.

Example of setting P to 10.42 on channel 1:

```json
{"command": "SET_KP", "channel": 1, "value": 10.42}
```

### SET_KI

The command `SET_KI` sets the I control term of the PID
controller for a channel. The value will be **cut** to two decimals.

Example of setting I to 5.2 on channel 1:

```json
{"command": "SET_KI", "channel": 1, "value": 5.2}
```

### SET_KD

The command `SET_KD` sets the D control term of the PID
controller for a channel. The value will be **cut** to two decimals.

Example of setting D to 0.37 on channel 1:

```json
{"command": "SET_KD", "channel": 1, "value": 0.37}
```

### SET_MODE

The command `SET_MODE` sets the output drive mode of a channel.
There are two possible modes to set (*note: three possible modes on the
Controller itself*):

- 0: Manual drive by setting the output with `SET_OUTPUT`.
- 1: Automatic PID-controlled drive.

Example of setting the drive mode to *manual* on channel 2:

```json
{"command": "SET_MODE", "channel": 2, "value": 0}
```

**Note:** The output speed should be explicitly set, with another command,
after setting the drive mode to manual. See the command below for setting speed
manually.

### SET_OUTPUT

The command `SET_OUTPUT` sets the output speed for a channel.
The speed should be between 0-255, where 0 means the lowest possible
speed a fan can go, and 255 the fastest speed. Only integers should be sent.

Example of setting the speed to 128 (50 %) on channel 2:

```json
{"command": "SET_OUTPUT", "channel": 2, "value": 128}
```

**Note:** The output speed will not be set unless the drive mode is set
to manual.

### GET_STATUS

The command `GET_STATUS` requests the Controller for current status (channel,
current temperature, target temperature, fan speed and raw output).

Example of getting the status of channel 2:

```json
{"command": "GET_STATUS", "channel": 2}
```

The status will be sent to the `channel_<number>_status` topic described in the
config file. It looks like this:

```json
{
  "temp": 0,
  "target": 30,
  "speed": 0,
  "output": 255
}
```

### GET_SETTINGS

The command `GET_SETTINGS` requests the Controller for current settings (channel,
mode, P, I and D tuning terms).

Example of getting the settings of channel 2:

```json
{"command": "GET_SETTINGS", "channel": 2}
```

The settings will be sent to the `channel_<number>_settings` topic described in the
config file. It looks like this:

```json
{
  "mode": 0,
  "kp": 4,
  "ki": 0.4,
  "kd": 2
}
```

**Note:** There are three possible modes for the Controller to be in:

- 0: Manual drive
- 1: Automatic drive
- 2: Forced FULL SPEED (usually caused by error reading temperature sensor)


# Development

There is a development Docker container provided for ensuring identical
development environments for each developer. This is also to lessen the
need for developers to install dependencies on their system (even though
venvs exist).

The port where the Arduino board resides must be provided as an environment
variable (this is to pass the port to the Docker container).
For example: `export ARDUINO_PORT=/dev/ttyACM0`.

Build the container with: `docker-compose build [--no-cache]` and run with
`docker-compose run dev`.

Docker and Docker Compose should obviously be installed, but those are
basically the only requirements for developer machines.

All development tasks should be run inside the container, unless otherwise
stated.

## Installing MQTTFanController in editable mode

All development tasks require installing MQTTFanController, since this
also installs all dependencies from PyPI.

During development it's quite useful to be able to run the app in
editable mode. This allows you to modify the code without reinstalling
the package every time there is a change to the source code. This can be
achieved by running `pip install -e .`.

## Running MQTTFanController inside the container

Before starting the bridge a configuration file must be provided. An example
config is provided above. If your MQTT broker requires username
and password to be provided, you may export them as environment variables
inside the container before starting the application:

```sh
export FANCONTROLBRIDGE_MQTTMESSENGER__USERNAME=username
export FANCONTROLBRIDGE_MQTTMESSENGER__PASSWORD=password
```

The app may be started simply by running `fancontrolbridge -c ./config.yaml`
after providing necessary configurations.

## Running unit tests

Unit tests can be run by running `python -m unittest`.

## Viewing logs during development

If you would like to view the logs outside the Docker container while
developing, there's an easy way to achieve it:

_Note: These should be run outside the container_

1. First get the running container id with: `docker ps`
2. Follow the logs with `docker logs <container-id> -f`
