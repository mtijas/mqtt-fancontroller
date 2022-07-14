#include "led.hpp"

Led::Led(Observable *events, int pin)
    : Component(events)
{
    led_pin = pin;
}

void Led::setup(String event_filter)
{
    this->event_filter = event_filter;
    pinMode(led_pin, OUTPUT);
    events->register_observer(this);
}

void Led::setup() {}

void Led::loop() {}

/**
 * @brief Callback for Observables to call when distributing events
 *
 * @param event
 * @param data
 */
void Led::notify(String event, String data)
{
    if (!event.equals(event_filter))
    {
        return;
    }

    if (data.equals("on"))
    {
        digitalWrite(led_pin, HIGH);
    }
    else
    {
        digitalWrite(led_pin, LOW);
    }
}
