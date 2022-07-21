#ifndef PIDCONTROLCOMPONENT_H
#define PIDCONTROLCOMPONENT_H

#include "Arduino.h"
#include <PID_v1.h>
#include "../utils/timedcomponent.hpp"

using namespace std;

class PIDControlComponent
    : public TimedComponent
{
private:
    char channel;

protected:
    bool automatic;
    double Kp;
    double Ki;
    double Kd;
    double *setpoint;
    double *input;
    double *output;
    PID *pid;

public:
    PIDControlComponent(
        Observable *events,
        PID *pid,
        int update_interval,
        const uint8_t channel,
        double *input,
        double *output,
        double *setpoint);
    void setup();
    void notify(const char *event, const uint8_t channel, const char *data);
    void update();
};

#endif
