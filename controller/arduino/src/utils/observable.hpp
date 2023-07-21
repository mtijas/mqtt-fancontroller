#ifndef OBSERVABLE_H
#define OBSERVABLE_H

#include "observer.hpp"
#include <Arduino.h>

class Observable {
  private:
    Observer *observers[50];
    int arr_length;

  public:
    void register_observer(Observer *observer);
    void notify_observers(const char *event, int payload);
};

#endif
