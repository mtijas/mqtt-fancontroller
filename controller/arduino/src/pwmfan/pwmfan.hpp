#ifndef PWMFAN_H
#define PWMFAN_H

#include "Arduino.h"
#include "../utils/timedcomponent.hpp"

using namespace std;

class PWMFan
    : public TimedComponent
{
private:
    int sense_pin;
    int pwm_pin;
    volatile int fan_pulses;

public:
    PWMFan(
        Observable *events,
        int update_interval,
        int sense_pin,
        int pwm_pin);
    void setup();
    void notify(const char *event, uint16_t payload);
    void update();
    void pickPulse();
};

#endif
