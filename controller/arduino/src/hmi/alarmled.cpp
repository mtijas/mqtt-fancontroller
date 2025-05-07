#include "alarmled.hpp"

AlarmLED::AlarmLED(Observable *events, int led_pin) : Component(events) {
    this->led_pin = led_pin;
}

void AlarmLED::setup() {
    pinMode(led_pin, OUTPUT);
    digitalWrite(led_pin, LOW);
    this->temp_high = false;
    this->fan_fail = false;
    this->sensor_fail = false;
    this->events->register_observer(this);
}

void AlarmLED::notify(const char *event, int payload) {
    if (strncmp(event, "alm_high_temp", 13) == 0) {
        temp_high = payload == 1 ? true : false;
    } else if (strncmp(event, "alm_fail_fan", 12) == 0) {
        fan_fail = payload == 1 ? true : false;
    } else if (strncmp(event, "alm_fail_sensor", 15) == 0) {
        sensor_fail = payload == 1 ? true : false;
    }

    if (temp_high || fan_fail || sensor_fail) {
        digitalWrite(led_pin, HIGH);
    } else {
        digitalWrite(led_pin, LOW);
    }
}

void AlarmLED::loop() { return; }
