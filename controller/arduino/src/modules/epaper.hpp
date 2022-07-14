#ifndef EPAPER_H
#define EPAPER_H

#include <Arduino.h>
#include "../utils/timedcomponent.hpp"
#include <SPI.h>
#include "../libs/epd1in54_V2.h"
#include "../libs/epdpaint.h"

#define RST_PIN 8
#define DC_PIN 9
#define CS_PIN 10
#define BUSY_PIN 7

#define COLORED 0
#define UNCOLORED 1

using namespace std;

class Epaper : public TimedComponent
{
protected:
    bool display_ok;

public:
    unsigned char image[1024];
    Paint *paint;
    Epd *epd;
    Epaper(Observable *events, int update_interval);
    void setup();
    void notify(String event, String data);
    void update();
};

#endif
