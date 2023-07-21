#ifndef PIDCONTROL_H
#define PIDCONTROL_H

#include "../utils/timedcomponent.hpp"
#include "Arduino.h"
#include <PID_v1.h>

using namespace std;

class PIDControl : public TimedComponent {
  protected:
    bool automatic;
    double Kp;
    double Ki;
    double Kd;
    double *setpoint;
    double *input;
    double *output;
    unsigned long previous_input_timestamp;
    bool notemp;
    PID *pid;

  public:
    PIDControl(Observable *events, PID *pid, int update_interval, double *input,
               double *output, double *setpoint);
    void setup();
    void notify(const char *event, int payload);
    void update();
};

#endif
