# mqtt-fancontroller

A MQTT-enabled fan controller for controlling native PWM computer fans
with Arduino's hardware PWM. Written in Python and C++.

## Install

There is currently no easy way to install the package since it's still
in early development phase (well, pip might offer something, but YMMV).

## Development

The project is divided in to two parts: the actual PID controller running
on Arduino, and the bridge Python app connecting Arduino serial port to MQTT
broker.

### Bridge

There is a development Docker container provided for ensuring identical
development environments for each developer. This is also to lessen the
need for developers to install dependencies on their system (even though
venvs exist).

Build the container with: `docker-compose build [--no-cache]` and run with
`docker-compose run dev`.

Docker and Docker Compose should obviously be installed, but those are
basically the only requirements for developer machines.

All development tasks should be run inside the container, unless otherwise
stated.

#### Installing MQTTFanController in editable mode

All development tasks require installing MQTTFanController, since this
also installs all dependencies from PyPI.

During development it's quite useful to be able to run the app in
editable mode. This allows you to modify the code without reinstalling
the package every time there is a change to the source code. This can be
achieved by running `pip install -e .`.

#### Running MQTTFanController inside the container

Before starting the bridge a configuration file must be provided. An example
config is provided as `config.yaml`. If your MQTT broker requires username
and password to be provided, you may export them as environment variables
inside the container before starting the application:

```sh
export MQTTFANCONTROLLER_MQTTMESSENGER__USERNAME=username
export MQTTFANCONTROLLER_MQTTMESSENGER__PASSWORD=password
```

The app may be started simply by running `mqttfancontroller -c ./config.yaml`
after providing necessary configurations.

#### Running unit tests

Unit tests can be run by running `python -m unittest`.

#### Viewing logs during development

If you would like to view the logs outside the Docker container while
developing, there's an easy way to achieve it:

_Note: These should be run outside the container_

1. First get the running container id with: `docker ps`
2. Follow the logs with `docker logs <container-id> -f`

### Controller

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
