# mqtt-fancontroller

A fan controller for controlling native PWM computer fans with Arduino's
hardware PWM, and a MQTT bridge for external control. Written in Python and C++.

The project is divided in to two parts: the actual PID controller running
on Arduino (*The Controller*), and the bridge Python app connecting Arduino serial port to MQTT
broker (*The Bridge*).

## The Bridge

### Description

The bridge acts as a middleman between a MQTT server and the Arduino-based
PID fan controller (connected via a serial port [USB] to the bridge). The bridge subscribes
to a command topic described in the config, and forwards the commands received in
that topic to the Controller via a serial port. The responses from the
Controller will be forwarded to the topics also described in the config.

### Installation

There is currently no easy way to install the package since it's still
in early development phase (well, pip might offer something, but YMMV).

### Configuration

The Bridge expects to find a config file in `$XDG_CONFIG_HOME/fancontrolbridge/config.yaml`.
This may be overridden by specifying a config file when starting the Bridge with
the flag `-c` (example: `fancontrolbridge -c ./config.yaml`).

## The Controller

### Description



# Running / deployment



# Development

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
