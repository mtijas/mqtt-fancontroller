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
        String data,
        int font_size,
        int y,
        int color,
        int background);
    void printLeftString(
        String data,
        int font_size,
        int y,
        int color,
        int background);
    void printRightString(
        String data,
        int font_size,
        int y,
        int color,
        int background);

public:
    Display(Observable *events, Epaper *epaper, int update_interval);
    void setup();
    void notify(String event, String data);
    void update();
};

#endif
