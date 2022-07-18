#ifndef MOMENTARYLED_H
#define MOMENTARYLED_H

#include <Arduino.h>
#include "led.hpp"

using namespace std;

class MomentaryLed : public Led
{
private:
    unsigned long on_counter;
    unsigned long last_millis;

protected:
    int on_duration;
    unsigned long calculate_duration(unsigned long start, unsigned long stop);

public:
    MomentaryLed(Observable *events, int led_pin, int on_duration);
    void loop();
    void notify(const String &event, const String &data);
};

#endif
