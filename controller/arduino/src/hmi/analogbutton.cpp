#include "analogbutton.hpp"

AnalogButton::AnalogButton(IObservable *events, int update_interval, int pin,
                           const char *lower_event, const char *upper_event)
    : TimedComponent(events, update_interval) {
    this->pin = pin;
    this->lower_event = lower_event;
    this->upper_event = upper_event;
}

void AnalogButton::setup() {
    this->prev_keyup_timestamp = millis();
    this->prev_event_timestamp = millis();
    this->key_pressed = false;
    this->events->register_observer(this);
}

void AnalogButton::notify(const char *event, int payload) {}

void AnalogButton::update() {
    unsigned long current_millis = millis();

    port_status = analogRead(pin);

    // No keys pressed
    if (port_status > 150 && port_status < 850) {
        prev_keyup_timestamp = current_millis;
        return;
    }

    if (calculate_elapsed(prev_keyup_timestamp, current_millis) < 50) {
        return;
    }

    if (calculate_elapsed(prev_event_timestamp, current_millis) > 500) {
        events->notify_observers(port_status < 512 ? lower_event : upper_event,
                                 pin);
        prev_event_timestamp = current_millis;
    }
}
