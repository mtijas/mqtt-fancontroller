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
    String channel;

protected:
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
        const String &channel,
        double *input,
        double *output,
        double *setpoint);
    void setup();
    void notify(const String &event, const String &data);
    void update();
};

#endif
