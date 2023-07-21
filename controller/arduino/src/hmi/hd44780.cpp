#include "hd44780.hpp"

HD44780::HD44780(Observable *events, int update_interval, int rs, int en,
                 int d4, int d5, int d6, int d7)
    : TimedComponent(events, update_interval) {
    this->rs = rs;
    this->en = en;
    this->d4 = d4;
    this->d5 = d5;
    this->d6 = d6;
    this->d7 = d7;
}

void HD44780::setup() {
    lcd = new LiquidCrystal(rs, en, d4, d5, d6, d7);
    lcd->begin(16, 2);
    lcd->print(" Fan Controller ");
    lcd->setCursor(0, 1);
    lcd->print("   Booting...   ");
    events->register_observer(this);
}

void HD44780::notify(const char *event, int payload) {
    float temporary = 0.0;

    if (strncmp(event, "temp", 4) == 0) {
        temporary = payload / 10.0;
        lcd->setCursor(2, 0);
        lcd->print("      ");
        lcd->setCursor(2, 0);
        lcd->print(temporary);
    } else if (strncmp(event, "target", 6) == 0) {
        temporary = payload / 10.0;
        lcd->setCursor(10, 0);
        lcd->print("      ");
        lcd->setCursor(10, 0);
        lcd->print(temporary);
    } else if (strncmp(event, "speed", 5) == 0) {
        lcd->setCursor(0, 1);
        lcd->print("    ");
        lcd->setCursor(0, 1);
        lcd->print(payload);
    } else if (strncmp(event, "output", 6) == 0) {
        lcd->setCursor(5, 1);
        lcd->print("   ");
        lcd->setCursor(5, 1);
        lcd->print(payload);
    } else if (strncmp(event, "mode", 4) == 0) {
        lcd->setCursor(9, 1);
        switch (payload) {
        case 0:
            lcd->print("MANU");
            break;
        case 1:
            lcd->print("AUTO");
            break;
        case 2:
            lcd->print("MAX!");
            break;
        default:
            lcd->print("ERR!");
            break;
        }
    } else if (strncmp(event, "alarm", 5) == 0) {
        lcd->setCursor(14, 1);
        lcd->print(1 == payload ? "AL" : "OK");
    } else if (strncmp(event, "bootup_complete", 15) == 0) {
        lcd->clear();
        lcd->setCursor(0, 0);
        lcd->print("T:      S:      ");
        lcd->setCursor(0, 1);
        lcd->print("    @   |       ");
    }
}

void HD44780::update() { return; }
