#ifndef MAXIM18B20_H
#define MAXIM18B20_H

#include "../utils/timedcomponent.hpp"
#include "Arduino.h"
#include <DS18B20.h>

using namespace std;

class Maxim18b20 : public TimedComponent {
  private:
    DS18B20 *sensor;
    int pin;

  public:
    Maxim18b20(Observable *events, DS18B20 *sensor, int update_interval,
               int port);
    void setup();
    void notify(const char *event, int payload);
    void update();
};

#endif
