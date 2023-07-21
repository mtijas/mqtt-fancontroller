#ifndef ALARMLED_H
#define ALARMLED_H

#include "../utils/component.hpp"
#include "Arduino.h"

using namespace std;

class AlarmLED : public Component {
  private:
    int led_pin;

  public:
    AlarmLED(Observable *events, int led_pin);
    void setup();
    void notify(const char *event, int payload);
    void loop();
};

#endif
