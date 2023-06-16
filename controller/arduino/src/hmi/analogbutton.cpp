#include "analogbutton.hpp"

AnalogButton::AnalogButton(
    Observable *events,
    int update_interval,
    int pin,
    int lower_code,
    int upper_code)
    : TimedComponent(events, update_interval)
{
    this->pin = pin;
    this->lower_code = lower_code;
    this->upper_code = upper_code;
}

void AnalogButton::setup()
{
    this->prev_keydn = millis();
    this->prev_keyup = millis();
    this->event_sent = false;
    this->key_pressed = false;
    this->events->register_observer(this);
}

void AnalogButton::notify(const char *event, uint16_t payload)
{
}

void AnalogButton::update()
{
    unsigned long current_millis = millis();

    port_status = analogRead(pin);

    // No keys pressed
    if (port_status > 150 && port_status < 850)
    {
        if (!event_sent)
        {
            return; // No events sent yet
        }

        // Key was pressed and is just released
        if (key_pressed)
        {
            prev_keyup = millis();
            key_pressed = false;
            return;
        }

        if (calculate_elapsed(prev_keyup, millis()) > 10)
        {
            event_sent = false;
        }
    }

    // At least one key is pressed

    if (!key_pressed)
    {
        prev_keydn = millis();
        key_pressed = true;
        return;
    }

    if (event_sent)
    {
        return; // Event already sent
    }

    if (calculate_elapsed(prev_keydn, millis()) > 10)
    {
        events->notify_observers(
            "keypress",
            port_status < 512 ? lower_code : upper_code);
        event_sent = true;
    }
}
