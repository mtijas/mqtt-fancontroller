#ifndef DISPLAY_H
#define DISPLAY_H

#include "../utils/timedcomponent.hpp"
#include "../components/epaper.hpp"

class Display : public TimedComponent
{
protected:
    Epaper *epaper;
    int width;
    int height;
    void printFullString(
        const String &data,
        int font_size,
        int y,
        int color,
        int background);
    void printLeftString(
        const String &data,
        int font_size,
        int y,
        int color,
        int background);
    void printRightString(
        const String &data,
        int font_size,
        int y,
        int color,
        int background);

public:
    Display(Observable *events, Epaper *epaper, int update_interval);
    void setup();
    void notify(const String &event, const String &data);
    void update();
};

#endif
