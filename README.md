# mqtt-fancontroller

A fan controller for controlling native PWM computer fans with Arduino's
hardware PWM, and a MQTT bridge for external control. Written in Python and C++.

## The Bridge

### Description

The bridge acts as a middleman between a MQTT server and the Arduino-based
controller (connected via a serial port [USB] to the bridge). The bridge subscribes
to a command topic described in the config, and forwards the commands received in
that topic to the Controller via a serial port. The responses from the
Controller will be forwarded to the topics also described in the config.

### Commands

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

"SET_TARGET": 64,
            "SET_OUTPUT": 65,
            "SET_KP": 66,
            "SET_KI": 67,
            "SET_KD": 68,
            "SET_MODE": 69,
            "GET_STATUS": 70,
            "GET_SETTINGS": 71,

#### SET_TARGET

The Command `SET_TARGET` sets a new target temperature for a channel.
The target temperature will be **cut** to one decimal (Example: 23.56 -> 23.5).
Use a period as decimal separator.

For example setting target temperature of 42.5 C to channel 1:

```json
{"command": "SET_TARGET", "channel": 1, "value": 42.5}
```

#### SET_KP



#### SET_KI



#### SET_KD



#### SET_MODE



#### SET_OUTPUT



#### GET_STATUS



#### GET_SETTINGS




### Installation

There is currently no easy way to install the package since it's still
in early development phase (well, pip might offer something, but YMMV).

### Configuration

#### The config file

The Bridge expects to find a config file in `$XDG_CONFIG_HOME/fancontrolbridge/config.yaml`.
This may be overridden by specifying a config file when starting the Bridge with
the flag `-c` (example: `fancontrolbridge -c ./config.yaml`).

Example of a full config file:

```yaml
modules:
  - type: mqttmessenger
    config:
      publish_events:
        controller_status: fancontrolbridge/status
        controller_settings: fancontrolbridge/settings
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

#### The MQTTMessenger config

##### `publish_events` and `subscribe_topics`

The configuration file allows setting command topic which the Bridge
will then listen for the commands, and the topics to which the responses
from the Controller should be forwarded to.

Command topic config example:

```yaml
subscribe_topics:
  - fancontrolbridge/commands
```

Response publish topics config example:

```yaml
publish_events:
  controller_status: fancontrolbridge/status
  controller_settings: fancontrolbridge/settings
  controller_command_results: fancontrolbridge/command-results
```

The commands received from the commands topics will be evaluated and sent
to the Controller if they are formed correctly. Evaluation results of all commands
and the results of sending the commands to the Controller commands will be forwarded
to the `controller_command_results` topic.

The responses from the Controller for `GET` commands will be forwarded to the topics
`controller_status` (for status report commands) and `controller_settings`
(for getting the current settings).

**To recap:**

- There will be a message in `controller_command_results` for *every* command
received from the command topics.
  - Listen to this to determine if any command got successfully forwarded.

- Sending `GET_STATUS` command results in a response to `controller_status`
topic containing current status (temps, rpm and output) of one channel on the Controller.

- Sending `GET_SETTINGS` command results in a response to `controller_settings`
topic containing current settings (mode and PID parameters) of one channel on the Controller.

##### Setting the MQTT broker host, username and password

The location of your MQTT broker must be set in `host: <mqtt_bridge_host>`.

If your MQTT broker requires username and password to be provided, you may
export them as environment variables inside the container before starting
the application (in Linux):

```sh
export FANCONTROLBRIDGE_MQTTMESSENGER__USERNAME=username
export FANCONTROLBRIDGE_MQTTMESSENGER__PASSWORD=password
```

####


### Running





# Development

The project is divided in to two parts: the actual PID controller running
on Arduino, and the bridge Python app connecting Arduino serial port to MQTT
broker.

## The Bridge

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

### Installing MQTTFanController in editable mode

All development tasks require installing MQTTFanController, since this
also installs all dependencies from PyPI.

During development it's quite useful to be able to run the app in
editable mode. This allows you to modify the code without reinstalling
the package every time there is a change to the source code. This can be
achieved by running `pip install -e .`.

### Running MQTTFanController inside the container

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

### Running unit tests

Unit tests can be run by running `python -m unittest`.

### Viewing logs during development

If you would like to view the logs outside the Docker container while
developing, there's an easy way to achieve it:

_Note: These should be run outside the container_

1. First get the running container id with: `docker ps`
2. Follow the logs with `docker logs <container-id> -f`

## The Controller

Arduino controller component has it's own Docker container for easier
uploading and compiling the code. The container may be built with
`docker-compose build [--no-cache]` and run with `docker-compose run
uploader`. This will automatically compile and upload the main.ino sketch.

In case you want to get inside the uploader without automatically compiling
and uploading the sketch, you may run `docker-compose run --entrypoint="bash"
uploader`. Then inside the container you may compile the sketch without
uploading it by running `arduino-cli compile --fqbn
${ARDUINO_PLATFORM}:${ARDUINO_BOARD} /controller/arduino`.

Inside the container you may also use `?` to communicate with Arduino's
serial interface. Just start minicom with `?`.
