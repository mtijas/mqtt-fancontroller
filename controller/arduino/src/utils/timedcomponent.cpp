#include "timedcomponent.hpp"
#include <limits.h>

TimedComponent::TimedComponent(Observable *events, int update_interval)
    : Component(events) {
    this->update_interval = update_interval;
}

void TimedComponent::loop() {
    unsigned long current_millis = millis();
    time_elapsed += calculate_elapsed(previous_millis, current_millis);

    if (time_elapsed >= update_interval) {
        update();
        time_elapsed = 0;
    }

    previous_millis = current_millis;
}

unsigned long TimedComponent::calculate_elapsed(unsigned long start,
                                                unsigned long stop) {
    if (stop < start) {
        return (ULONG_MAX - start) + stop;
    }
    return stop - start;
}
