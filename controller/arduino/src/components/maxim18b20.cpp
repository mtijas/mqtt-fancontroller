#include "Arduino.h"
#include "maxim18b20.hpp"

Maxim18b20::Maxim18b20(Observable *events, DS18B20 *ds, int update_interval, int pin)
    : TimedComponent(events, update_interval)
{
    this->pin = pin;
    this->ds = ds;
}

void Maxim18b20::setup() {}

void Maxim18b20::notify(String event, String data) {}

void Maxim18b20::update()
{
    int number = 1;
    String temp;

    events->notify_observers("d1", "on");

    while (ds->selectNext())
    {
        events->notify_observers("d2", "on");
        temp = ds->getTempC();
        events->notify_observers("temp-" + String(number), temp);
        number++;
    }
}
