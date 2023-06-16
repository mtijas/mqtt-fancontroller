#ifndef ALARMLED_H
#define ALARMLED_H

#include "Arduino.h"
#include "../utils/component.hpp"

using namespace std;

class AlarmLED
    : public Component
{
private:
    int led_pin;

public:
    AlarmLED(
        Observable *events,
        int led_pin);
    void setup();
    void notify(const char *event, uint16_t payload);
    void loop();
};

#endif
