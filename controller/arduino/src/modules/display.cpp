#include "../version.hpp"
#include "display.hpp"
#include "../utils/timedcomponent.hpp"

Display::Display(Observable *events, Epaper *epaper, int update_interval)
    : TimedComponent(events, update_interval)
{
    this->epaper = epaper;
    this->width = epaper->getWidth();
    this->height = epaper->getHeight();
}

void Display::setup()
{
    events->register_observer(this);

    epaper->setup();
    epaper->clearDisplay();
    printLeftString("Channel 1", 12, 0, UNCOLORED, COLORED);
    printRightString("Channel 2", 12, 0, UNCOLORED, COLORED);
    printLeftString("Temperature", 12, 16, COLORED, UNCOLORED);
    printRightString("Temperature", 12, 16, COLORED, UNCOLORED);
    printLeftString("Temp target", 12, 56, COLORED, UNCOLORED);
    printRightString("Temp target", 12, 56, COLORED, UNCOLORED);
    printLeftString("Fan speed", 12, 96, COLORED, UNCOLORED);
    printRightString("Fan speed", 12, 96, COLORED, UNCOLORED);
    printLeftString("Output (%)", 12, 136, COLORED, UNCOLORED);
    printRightString("Output (%)", 12, 136, COLORED, UNCOLORED);
    epaper->fullUpdate();
}

void Display::update()
{
    epaper->fullUpdate();
}

void Display::notify(const char *event, const uint8_t channel, const char *data)
{
    char buffer[7];
    if (strncmp(event, "temp", 4) == 0 && channel == 1)
    {
        printLeftString(data, 20, 32, COLORED, UNCOLORED);
    }
    else if (strncmp(event, "temp", 4) == 0 && channel == 2)
    {
        printRightString(data, 20, 32, COLORED, UNCOLORED);
    }
    else if (strncmp(event, "target", 6) == 0 && channel == 1)
    {
        printLeftString(data, 20, 72, COLORED, UNCOLORED);
    }
    else if (strncmp(event, "target", 6) == 0 && channel == 2)
    {
        printRightString(data, 20, 72, COLORED, UNCOLORED);
    }
    else if (strncmp(event, "speed", 5) == 0 && channel == 1)
    {
        printLeftString(data, 20, 112, COLORED, UNCOLORED);
    }
    else if (strncmp(event, "speed", 5) == 0 && channel == 2)
    {
        printRightString(data, 20, 112, COLORED, UNCOLORED);
    }
    else if (strncmp(event, "output", 6) == 0 && channel == 1)
    {
        float data_fl = atof(data);
        float percent = data_fl / 255 * 100;
        dtostrf(percent, 1, 1, buffer);
        printLeftString(buffer, 20, 152, COLORED, UNCOLORED);
    }
    else if (strncmp(event, "output", 6) == 0 && channel == 2)
    {
        float data_fl = atof(data);
        float percent = data_fl / 255 * 100;
        dtostrf(percent, 1, 1, buffer);
        printRightString(buffer, 20, 152, COLORED, UNCOLORED);
    }
    else if (strncmp(event, "mode", 4) == 0 && channel == 1)
    {
        if (strncmp(data, "0", 1) == 0)
        {
            printLeftString("MANUAL", 20, 176, COLORED, UNCOLORED);
        }
        else
        {
            printLeftString("Auto", 20, 176, COLORED, UNCOLORED);
        }
    }
    else if (strncmp(event, "mode", 4) == 0 && channel == 2)
    {
        if (strncmp(data, "0", 1) == 0)
        {
            printRightString("MANUAL", 20, 176, COLORED, UNCOLORED);
        }
        else
        {
            printRightString("Auto", 20, 176, COLORED, UNCOLORED);
        }
    }
}

void Display::printFullString(const char *data, int font_size, int y, int color, int background)
{
    epaper->printString(data, font_size, 0, y, width, color, background);
}

void Display::printLeftString(const char *data, int font_size, int y, int color, int background)
{
    int total_width = width / 2;
    epaper->printString(data, font_size, 0, y, total_width, color, background);
}

void Display::printRightString(const char *data, int font_size, int y, int color, int background)
{
    int x = width / 2 + 4;
    int total_width = width / 2 - 4;
    epaper->printString(data, font_size, x, y, total_width, color, background);
}
