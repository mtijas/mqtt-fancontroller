#include "memory.hpp"

Memory::Memory(Observable *events, int update_interval)
    : TimedComponent(events, update_interval) {
    return;
}

void Memory::setup() {
    this->temp_target = 0;
    this->kp = 0;
    this->ki = 0;
    this->kd = 0;
    this->mode = 0;
    this->events->register_observer(this);
}

void Memory::notify(const char *event, int payload) {
    if (strncmp(event, "target", 6) == 0) {
        if (temp_target == payload) {
            return;
        }
        temp_target = payload;
        events->notify_observers("pending_write", 1);
    } else if (strncmp(event, "kp", 2) == 0) {
        if (kp == payload) {
            return;
        }
        kp = payload;
        events->notify_observers("pending_write", 1);
    } else if (strncmp(event, "ki", 2) == 0) {
        if (ki == payload) {
            return;
        }
        ki = payload;
        events->notify_observers("pending_write", 1);
    } else if (strncmp(event, "kd", 2) == 0) {
        if (kd == payload) {
            return;
        }
        kd = payload;
        events->notify_observers("pending_write", 1);
    } else if (strncmp(event, "mode", 4) == 0) {
        if (mode == payload) {
            return;
        }
        mode = payload;
        events->notify_observers("pending_write", 1);
    } else if (strncmp(event, "write_memory", 12) == 0) {
        EEPROM.put(0, temp_target);
        EEPROM.put(1*sizeof(float), kp);
        EEPROM.put(2*sizeof(float), ki);
        EEPROM.put(3*sizeof(float), kd);
        EEPROM.put(4*sizeof(float), mode);
    } else if (strncmp(event, "read_memory", 11) == 0) {
        EEPROM.get(0, temp_target);
        EEPROM.get(1*sizeof(float), kp);
        EEPROM.get(2*sizeof(float), ki);
        EEPROM.get(3*sizeof(float), kd);
        EEPROM.get(4*sizeof(float), mode);
        events->notify_observers("target", temp_target);
        events->notify_observers("kp", kp);
        events->notify_observers("ki", ki);
        events->notify_observers("kd", kd);
        events->notify_observers("mode", mode);
    }
}

void Memory::update() { return; }
