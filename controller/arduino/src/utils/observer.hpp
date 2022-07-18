#ifndef OBSERVER_H
#define OBSERVER_H

#include <Arduino.h>

using namespace std;

class Observer
{
public:
    virtual void notify(const String &event, const String &data) = 0;
};

#endif
