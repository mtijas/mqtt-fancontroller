#ifndef HD44780_H
#define HD44780_H

#include "Arduino.h"
#include <LiquidCrystal.h>
#include "../utils/timedcomponent.hpp"

using namespace std;

class HD44780
    : public TimedComponent
{
private:
    int rs;
    int en;
    int d4;
    int d5;
    int d6;
    int d7;
    LiquidCrystal *lcd;
    char temp[6], target[6];
    int speed, output, mode;
    bool alarm;

public:
    HD44780(
        Observable *events,
        int update_interval,
        int rs,
        int en,
        int d4,
        int d5,
        int d6,
        int d7);
    void setup();
    void notify(const char *event, uint16_t payload);
    void update();
};

#endif
