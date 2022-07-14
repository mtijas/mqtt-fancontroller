#include <limits.h>
#include "momentaryled.hpp"

MomentaryLed::MomentaryLed(Observable *events, int led_pin, int on_duration)
: Led(events, led_pin)
{
    this->on_duration = on_duration;
}

void MomentaryLed::loop()
{
    unsigned long current_millis = millis();
    this->on_counter += calculate_duration(last_millis, current_millis);

    if (this->on_counter >= on_duration)
    {
        digitalWrite(led_pin, LOW);
    }

    this->last_millis = current_millis;
}

unsigned long MomentaryLed::calculate_duration(unsigned long start, unsigned long stop)
{
    if (stop < start)
    {
        return (ULONG_MAX - start) + stop;
    }
    return stop - start;
}

void MomentaryLed::notify(String event, String data)
{
    if (!event.equals(event_filter))
    {
        return;
    }
    digitalWrite(led_pin, HIGH);
    this->on_counter = 0;
}
