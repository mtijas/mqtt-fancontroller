#ifndef ANALOGBUTTON_H
#define ANALOGBUTTON_H

#include "../utils/timedcomponent.hpp"
#include "Arduino.h"

using namespace std;

class AnalogButton : public TimedComponent {
  protected:
    int pin, port_status, lower_code, upper_code;
    unsigned long prev_keydn, prev_keyup;
    bool event_sent, key_pressed;

  public:
    AnalogButton(Observable *events, int update_interval, int pin,
                 int lower_code, int upper_code);
    void setup();
    void notify(const char *event, int payload);
    void update();
};

#endif
