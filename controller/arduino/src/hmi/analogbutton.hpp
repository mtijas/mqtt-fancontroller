#ifndef ANALOGBUTTON_H
#define ANALOGBUTTON_H

#include "../utils/timedcomponent.hpp"
#include "Arduino.h"

using namespace std;

class AnalogButton : public TimedComponent {
  protected:
    int pin, port_status;
    unsigned long prev_keyup_timestamp, prev_event_timestamp;
    bool key_pressed;
    const char *lower_event, *upper_event;

  public:
    AnalogButton(IObservable *events, int update_interval, int pin,
                 const char *lower_event, const char *upper_event);
    void setup();
    void notify(const char *event, int payload);
    void update();
};

#endif
