#ifndef OBSERVER_H
#define OBSERVER_H

#include <Arduino.h>

using namespace std;

class Observer
{
public:
    virtual void notify(const char *event, const uint8_t channel, const char *data) = 0;
};

#endif
