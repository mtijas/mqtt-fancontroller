#ifndef OBSERVER_H
#define OBSERVER_H

#include <Arduino.h>

using namespace std;

class Observer
{
public:
    virtual void notify(String event, String data) = 0;
};

#endif
