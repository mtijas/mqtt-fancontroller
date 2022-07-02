# mqtt-fancontroller
A MQTT-enabled fan controller for controlling native PWM computer fans 
with Raspberry Pi's hardware PWM. Written in Python.

## Development

There is a development Docker container provided for ensuring identical 
development environments for each developer. This is also to lessen the
need for developers to install dependencies on their system (even though
venvs exist).

Build the container with: `docker-compose build` and run with 
`docker-compose run dev`.

Docker and Docker Compose should obviously be installed, but those are
basically the only requirements for developer machines.

### Running MQTTFanController inside the container

1. Install the app with `pip install .`
2. Run with: `mqttfancontroller`


