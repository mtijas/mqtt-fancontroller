#include "maxim18b20.hpp"

Maxim18b20::Maxim18b20(Observable *events, DS18B20 *ds, int update_interval, int pin)
    : TimedComponent(events, update_interval)
{
    this->pin = pin;
    this->ds = ds;
}

void Maxim18b20::setup() {}

void Maxim18b20::notify(const char *event, uint16_t payload) {}

void Maxim18b20::update()
{
    float temp;
    uint16_t payload;

    while (ds->selectNext())
    {
        temp = ds->getTempC();
        payload = (int)(temp * 10.0 + 32768);
        events->notify_observers("temp", payload);
    }
}
