#ifndef ANALOGBUTTON_H
#define ANALOGBUTTON_H

#include "Arduino.h"
#include "../utils/timedcomponent.hpp"

using namespace std;

class AnalogButton
    : public TimedComponent
{
protected:
    int pin, port_status, lower_code, upper_code;
    unsigned long prev_keydn, prev_keyup;
    bool event_sent, key_pressed;

public:
    AnalogButton(Observable *events, int update_interval, int pin, int lower_code, int upper_code);
    void setup();
    void notify(const char *event, uint16_t payload);
    void update();
};

#endif
