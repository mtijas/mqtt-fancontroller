#ifndef HD44780_H
#define HD44780_H

#include "../utils/timedcomponent.hpp"
#include "Arduino.h"
#include <LiquidCrystal.h>

using namespace std;

class HD44780 : public TimedComponent {
  private:
    int rs;
    int en;
    int d4;
    int d5;
    int d6;
    int d7;
    LiquidCrystal *lcd;

  public:
    HD44780(Observable *events, int update_interval, int rs, int en, int d4,
            int d5, int d6, int d7);
    void setup();
    void notify(const char *event, int payload);
    void update();
};

#endif
