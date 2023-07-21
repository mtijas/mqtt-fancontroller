#ifndef PWMFAN_H
#define PWMFAN_H

#include "../utils/timedcomponent.hpp"
#include "Arduino.h"

using namespace std;

class PWMFan : public TimedComponent {
  private:
    int sense_pin;
    int pwm_pin;
    volatile int fan_pulses;

  public:
    PWMFan(Observable *events, int update_interval, int sense_pin, int pwm_pin);
    void setup();
    void notify(const char *event, int payload);
    void update();
    void pickPulse();
};

#endif
