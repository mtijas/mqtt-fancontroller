#ifndef EPAPER_H
#define EPAPER_H

#include <Arduino.h>
#include <SPI.h>
#include "../libs/epd1in54_V2.h"
#include "../libs/epdpaint.h"

#define COLORED 0
#define UNCOLORED 1

using namespace std;

class Epaper
{
protected:
    bool display_ok;
    sFONT *getFont(int font_size);
    Paint *paint;
    Epd *epd;
    int width;
    int height;

public:
    Epaper(Paint *paint, Epd *epd, int width, int height);
    void setup();
    int getWidth();
    int getHeight();
    void clearDisplay();
    void fullUpdate();
    void partUpdate();
    void printString(
        const String &data,
        int font_size,
        int x,
        int y,
        int width);
    void printString(
        const String &data,
        int font_size,
        int x,
        int y,
        int width,
        int color,
        int background);
};

#endif
