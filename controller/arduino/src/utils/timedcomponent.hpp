#ifndef TIMEDCOMPONENT_H
#define TIMEDCOMPONENT_H

#include "component.hpp"

class TimedComponent : public Component
{
private:
    unsigned long previous_millis;

protected:
    int update_interval;
    unsigned long time_elapsed;
    unsigned long calculate_elapsed(unsigned long start, unsigned long stop);

public:
    TimedComponent(Observable *events, int update_interval);
    virtual void update() = 0;
    void loop();
};

#endif
