#ifndef OBSERVER_H
#define OBSERVER_H

#include <Arduino.h>

using namespace std;

class Observer
{
public:
    virtual void notify(const char *event, uint16_t payload) = 0;
};

#endif
