#ifndef IOBSERVABLE_H
#define IOBSERVABLE_H

#include "observer.hpp"
#include <Arduino.h>

class IObservable {
  private:
    Observer *observers[50];
    int observers_length;

  public:
    IObservable();
    virtual void register_observer(Observer *observer) = 0;
    virtual void notify_observers(const char *event, int payload) = 0;
};

#endif
