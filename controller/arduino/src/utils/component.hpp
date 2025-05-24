#ifndef COMPONENT_H
#define COMPONENT_H

#include "iobservable.hpp"

class Component : public Observer {
  protected:
    IObservable *events;

  public:
    Component(IObservable *events);
    virtual void setup() = 0;
    virtual void loop() = 0;
};

#endif
