#include "maxim18b20.hpp"

Maxim18b20::Maxim18b20(Observable *events, DS18B20 *sensor, int update_interval,
                       int pin)
    : TimedComponent(events, update_interval) {
    this->pin = pin;
    this->sensor = sensor;
}

void Maxim18b20::setup() {}

void Maxim18b20::notify(const char *event, int payload) {}

void Maxim18b20::update() {
    float temp;
    int payload;

    while (sensor->selectNext()) {
        temp = sensor->getTempC();
        payload = (int)(temp * 10.0);
        events->notify_observers("temp", payload);
    }
}
