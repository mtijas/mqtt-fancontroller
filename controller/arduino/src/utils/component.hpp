#ifndef COMPONENT_H
#define COMPONENT_H

#include "observable.hpp"

class Component : public Observer {
  protected:
    Observable *events;

  public:
    Component(Observable *events);
    virtual void setup() = 0;
    virtual void loop() = 0;
};

#endif
