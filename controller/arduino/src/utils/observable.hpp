#ifndef OBSERVABLE_H
#define OBSERVABLE_H

#include <Arduino.h>
#include "observer.hpp"

class Observable
{
private:
    Observer* observers[50];
    int arr_length;

public:
    void register_observer(Observer* observer);
    void notify_observers(const String &event, const String &data);
};

#endif
