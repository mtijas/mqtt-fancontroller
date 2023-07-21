#include "alarmled.hpp"

AlarmLED::AlarmLED(Observable *events, int led_pin) : Component(events) {
    this->led_pin = led_pin;
}

void AlarmLED::setup() {
    pinMode(led_pin, OUTPUT);
    digitalWrite(led_pin, LOW);
    this->events->register_observer(this);
}

void AlarmLED::notify(const char *event, int payload) {
    if (strncmp(event, "alarm", 5) == 0) {
        digitalWrite(led_pin, payload ? HIGH : LOW);
    }
}

void AlarmLED::loop() {}
