#include "maxim18b20.hpp"

Maxim18b20::Maxim18b20(Observable *events, DS18B20 *ds, int update_interval, int pin)
    : TimedComponent(events, update_interval)
{
    this->pin = pin;
    this->ds = ds;
}

void Maxim18b20::setup() {}

void Maxim18b20::notify(const char *event, const uint8_t channel, const char *data) {}

void Maxim18b20::update()
{
    int number = 1;
    float temp;
    int result;
    char data[8];

    while (ds->selectNext())
    {
        temp = ds->getTempC();

        dtostrf(temp, 1, 1, data);

        events->notify_observers("temp", number, data);
        number++;
    }
}
