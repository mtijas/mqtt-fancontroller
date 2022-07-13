#!/bin/sh

echo "\nArduino-cli board list:"
arduino-cli board list

echo "\nInstalling platform ${ARDUINO_PLATFORM}"
arduino-cli core install ${ARDUINO_PLATFORM}

echo "\nCompiling 'src/src.ino'"
arduino-cli compile --fqbn ${ARDUINO_PLATFORM}:${ARDUINO_BOARD} ./src/src.ino

echo "\nUploading to ${ARDUINO_BOARD} via ${ARDUINO_PORT} (mapped to /dev/ttyACM0 in the container)"
arduino-cli upload -p /dev/ttyACM0 --fqbn ${ARDUINO_PLATFORM}:${ARDUINO_BOARD} ./src/src.ino
echo "Upload process finished. Exiting..."
