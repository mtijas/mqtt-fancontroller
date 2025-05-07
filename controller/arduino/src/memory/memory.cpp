#include "memory.hpp"

Memory::Memory(Observable *events, int update_interval)
    : TimedComponent(events, update_interval) {
    return;
}

void Memory::setup() {
    this->temp_target = 0;
    this->events->register_observer(this);
}

void Memory::notify(const char *event, int payload) {
    if (strncmp(event, "target", 6) == 0) {
        if (temp_target == payload) {
            return;
        }
        temp_target = payload;
        events->notify_observers("pending_write", 1);
    } else if (strncmp(event, "write_memory", 12) == 0) {
        EEPROM.put(0, temp_target);
    } else if (strncmp(event, "read_memory", 11) == 0) {
        EEPROM.get(0, temp_target);
        events->notify_observers("target", temp_target);
    }
}

void Memory::update() { return; }
