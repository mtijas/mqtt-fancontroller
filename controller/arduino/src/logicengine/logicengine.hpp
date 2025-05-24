#ifndef LOGICENGINE_H
#define LOGICENGINE_H

#include "../utils/timedcomponent.hpp"
#include "Arduino.h"

using namespace std;

class LogicEngine : public TimedComponent {
  private:
    int temp_target;

  public:
    LogicEngine(IObservable *events, int update_interval);
    void setup();
    void notify(const char *event, int payload);
    void update();
};

#endif
