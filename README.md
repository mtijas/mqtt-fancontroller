# mqtt-fancontroller

A MQTT-enabled fan controller for controlling native PWM computer fans
with Raspberry Pi's hardware PWM. Written in Python.

## Install

There is currently no easy way to install the package since it's still
in early development phase (well, pip might offer something, but YMMV).

## Development

There is a development Docker container provided for ensuring identical
development environments for each developer. This is also to lessen the
need for developers to install dependencies on their system (even though
venvs exist).

Build the container with: `docker-compose build --no-cache` and run with
`docker-compose run dev`.

Docker and Docker Compose should obviously be installed, but those are
basically the only requirements for developer machines.

### Running MQTTFanController inside the container

During development it's quite useful to be able to run the app in
editable mode. This allows you to modify the code without reinstalling
the package every time there is a change to the source code.

1. Install the app with `pip install -e .`
2. Run with: `mqttfancontroller`

### Running unit tests

Unit tests can simply be run by running `python -m unittest` inside the
container.

### Viewing logs during development

If you would like to view the logs outside the Docker container while
developing, there's an easy way to achieve it:

_Note: These should be run outside the container_

1. First get the running container id with: `docker ps`
2. Follow the logs with `docker logs <container-id> -f`
