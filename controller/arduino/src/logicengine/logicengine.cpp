#include "logicengine.hpp"

LogicEngine::LogicEngine(Observable *events, int update_interval)
    : TimedComponent(events, update_interval) {
    return;
}

void LogicEngine::setup() {
    this->temp_target = 0;
    this->events->register_observer(this);
}

void LogicEngine::notify(const char *event, int payload) {
    if (strncmp(event, "btn_up", 6) == 0) {
        events->notify_observers("target", temp_target + 1);
    } else if (strncmp(event, "btn_dn", 6) == 0) {
        events->notify_observers("target", temp_target - 1);
    } else if (strncmp(event, "target", 6) == 0) {
        temp_target = payload;
    }
}

void LogicEngine::update() { return; }
