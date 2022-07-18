#ifndef PWMFAN_H
#define PWMFAN_H

#include "Arduino.h"
#include "../utils/timedcomponent.hpp"

using namespace std;

class PWMFan
    : public TimedComponent
{
private:
    String channel;
    int sense_pin;
    int pwm_pin;
    int fan_pulses;

public:
    PWMFan(
        Observable *events,
        int update_interval,
        int sense_pin,
        int pwm_pin,
        const String &channel);
    void setup();
    void notify(const String &event, const String &data);
    void update();
    void pickPulse();
};

#endif
