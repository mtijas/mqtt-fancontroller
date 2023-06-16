#include "hd44780.hpp"

HD44780::HD44780(
    Observable *events,
    int update_interval,
    int rs,
    int en,
    int d4,
    int d5,
    int d6,
    int d7)
    : TimedComponent(events, update_interval)
{
    this->rs = rs;
    this->en = en;
    this->d4 = d4;
    this->d5 = d5;
    this->d6 = d6;
    this->d7 = d7;
}

void HD44780::setup()
{
    lcd = new LiquidCrystal(rs, en, d4, d5, d6, d7);
    lcd->begin(16, 2);
    lcd->print(" Fan Controller ");
    lcd->setCursor(0, 1);
    lcd->print("   Booting...   ");
    events->register_observer(this);
}

void HD44780::notify(const char *event, uint16_t payload)
{
    float temporary = 0.0;

    if (strncmp(event, "temp", 4) == 0)
    {
        temporary = (double)(payload - 32768) / 10.0;
        dtostrf(temporary, 5, 1, temp);
    }
    else if (strncmp(event, "target", 6) == 0)
    {
        temporary = (double)(payload - 32768) / 10.0;
        dtostrf(temporary, 5, 1, target);
    }
    else if (strncmp(event, "speed", 5) == 0)
    {
        speed = payload;
    }
    else if (strncmp(event, "output", 6) == 0)
    {
        output = payload;
    }
    else if (strncmp(event, "mode", 4) == 0)
    {
        mode = payload;
    }
    else if (strncmp(event, "alarm", 5) == 0)
    {
        alarm = payload ? true : false;
    }
    else if (strncmp(event, "bootup_complete", 15) == 0)
    {
        lcd->clear();
    }
}

void HD44780::update()
{
    char message[17];
    lcd->setCursor(0, 0);
    snprintf(message, 9, "T:%s ", temp);
    lcd->print(message);

    lcd->setCursor(8, 0);
    snprintf(message, 9, "S:%s ", target);
    lcd->print(message);

    lcd->setCursor(0, 1);
    snprintf(message, 17, "F:%4d@%3d %s", speed, output, alarm ? "ALARM" : "   OK");
    lcd->print(message);
}
