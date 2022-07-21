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

void Display::notify(const String &event, const String &data)
{
    if (event.equals("ch1-temp"))
    {
        printLeftString(data, 20, 32, COLORED, UNCOLORED);
    }
    else if (event.equals("ch2-temp"))
    {
        printRightString(data, 20, 32, COLORED, UNCOLORED);
    }
    else if (event.equals("ch1-target"))
    {
        printLeftString(data, 20, 72, COLORED, UNCOLORED);
    }
    else if (event.equals("ch2-target"))
    {
        printRightString(data, 20, 72, COLORED, UNCOLORED);
    }
    else if (event.equals("ch1-speed"))
    {
        printLeftString(data, 20, 112, COLORED, UNCOLORED);
    }
    else if (event.equals("ch2-speed"))
    {
        printRightString(data, 20, 112, COLORED, UNCOLORED);
    }
    else if (event.equals("ch1-output"))
    {
        float percent = data.toFloat() / 255 * 100;
        printLeftString(String(percent), 20, 152, COLORED, UNCOLORED);
    }
    else if (event.equals("ch2-output"))
    {
        float percent = data.toFloat() / 255 * 100;
        printRightString(String(percent), 20, 152, COLORED, UNCOLORED);
    }
    else if (event.equals("ch1-mode"))
    {
        if (data.equals("0"))
        {
            printLeftString("MANUAL", 20, 176, COLORED, UNCOLORED);
        }
        else
        {
            printLeftString("Auto", 20, 176, COLORED, UNCOLORED);
        }
    }
    else if (event.equals("ch2-mode"))
    {
        if (data.equals("0"))
        {
            printRightString("MANUAL", 20, 176, COLORED, UNCOLORED);
        }
        else
        {
            printRightString("Auto", 20, 176, COLORED, UNCOLORED);
        }
    }
}

void Display::printFullString(const String &data, int font_size, int y, int color, int background)
{
    epaper->printString(data, font_size, 0, y, width, color, background);
}

void Display::printLeftString(const String &data, int font_size, int y, int color, int background)
{
    int total_width = width / 2;
    epaper->printString(data, font_size, 0, y, total_width, color, background);
}

void Display::printRightString(const String &data, int font_size, int y, int color, int background)
{
    int x = width / 2 + 4;
    int total_width = width / 2 - 4;
    epaper->printString(data, font_size, x, y, total_width, color, background);
}
