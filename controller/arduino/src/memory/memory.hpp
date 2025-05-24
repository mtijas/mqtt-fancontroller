#ifndef MEMORY_H
#define MEMORY_H

#include "../utils/timedcomponent.hpp"
#include "Arduino.h"
#include <EEPROM.h>

using namespace std;

class Memory : public TimedComponent {
  private:
    int temp_target, kp, ki, kd, mode;
    bool needs_saving = false;

  public:
    Memory(IObservable *events, int update_interval);
    void setup();
    void notify(const char *event, int payload);
    void update();
};

#endif
