#ifndef MAXIM18B20_H
#define MAXIM18B20_H

#include "Arduino.h"
#include <DS18B20.h>
#include "../utils/timedcomponent.hpp"

using namespace std;

class Maxim18b20
: public TimedComponent
{
private:
    DS18B20 *ds;
    int pin;

public:
    Maxim18b20(Observable *events, DS18B20 *ds, int update_interval, int port);
    void setup();
    void notify(const char *event, const uint8_t channel, const char *data);
    void update();
};

#endif
