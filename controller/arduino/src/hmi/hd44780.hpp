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

  protected:
    void print_fmt(int column, int row, const char *message, const char *placeholder);
    void print_fmt(int column, int row, float message, const char *placeholder);
    void print_fmt(int column, int row, int message, const char *placeholder);
    void prepare_print_position(int column, int row, const char *placeholder);

  public:
    HD44780(IObservable *events, int update_interval, int rs, int en, int d4,
            int d5, int d6, int d7);
    void setup();
    void notify(const char *event, int payload);
    void update();
};

#endif
