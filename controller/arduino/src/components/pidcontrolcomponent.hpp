#ifndef PIDCONTROLCOMPONENT_H
#define PIDCONTROLCOMPONENT_H

#include "Arduino.h"
#include <AutoPID.h>
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
    AutoPID *pid;
    bool invert;

public:
    PIDControlComponent(
        Observable *events,
        AutoPID *pid,
        int update_interval,
        const String &channel,
        double *input,
        double *output,
        double *setpoint,
        bool invert);
    void setup();
    void notify(const String &event, const String &data);
    void update();
};

#endif
