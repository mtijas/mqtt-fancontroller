#ifndef PWMFAN_H
#define PWMFAN_H

#include "../utils/timedcomponent.hpp"

using namespace std;

class PWMFan
    : public TimedComponent
{
private:
    int channel;
    int sense_pin;
    int pwm_pin;
    int fan_pulses;

public:
    PWMFan(Observable *events, int update_interval, int sense_pin, int pwm_pin, int channel);
    void setup();
    void notify(String event, String data);
    void update();
    void pickPulse();
};

#endif
