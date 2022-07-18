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
    printFullString(
        "MQTTFanController " + String(__MFC_VERSION__),
        12,
        0,
        UNCOLORED,
        COLORED);
    printLeftString("Channel 1", 12, 16, UNCOLORED, COLORED);
    printRightString("Channel 2", 12, 16, UNCOLORED, COLORED);
    printLeftString("Temperature", 12, 32, COLORED, UNCOLORED);
    printRightString("Temperature", 12, 32, COLORED, UNCOLORED);
    printLeftString("Temp target", 12, 72, COLORED, UNCOLORED);
    printRightString("Temp target", 12, 72, COLORED, UNCOLORED);
    printLeftString("Fan speed", 12, 112, COLORED, UNCOLORED);
    printRightString("Fan speed", 12, 112, COLORED, UNCOLORED);
    printLeftString("Output (%)", 12, 152, COLORED, UNCOLORED);
    printRightString("Output (%)", 12, 152, COLORED, UNCOLORED);
    epaper->fullUpdate();
}

void Display::update()
{
    epaper->fullUpdate();
}

void Display::notify(String event, String data)
{
    if (event.equals("temp-1"))
    {
        printLeftString(data, 20, 48, COLORED, UNCOLORED);
    }
    else if (event.equals("temp-2"))
    {
        printRightString(data, 20, 48, COLORED, UNCOLORED);
    }
}

void Display::printFullString(String data, int font_size, int y, int color, int background)
{
    epaper->printString(data, font_size, 0, y, width, color, background);
}

void Display::printLeftString(String data, int font_size, int y, int color, int background)
{
    int total_width = width / 2;
    epaper->printString(data, font_size, 0, y, total_width, color, background);
}

void Display::printRightString(String data, int font_size, int y, int color, int background)
{
    int x = width / 2 + 2;
    int total_width = width / 2 - 2;
    epaper->printString(data, font_size, x, y, total_width, color, background);
}
