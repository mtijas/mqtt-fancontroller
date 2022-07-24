#ifndef PWMFAN_H
#define PWMFAN_H

#include "Arduino.h"
#include "../utils/timedcomponent.hpp"

using namespace std;

class PWMFan
    : public TimedComponent
{
private:
    char channel;
    int sense_pin;
    int pwm_pin;
    volatile int fan_pulses;

public:
    PWMFan(
        Observable *events,
        int update_interval,
        int sense_pin,
        int pwm_pin,
        const uint8_t channel);
    void setup();
    void notify(const char *event, const uint8_t channel, const char *data);
    void update();
    void pickPulse();
};

#endif
