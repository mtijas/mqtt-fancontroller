#ifndef LED_H
#define LED_H

#include <Arduino.h>
#include "../utils/component.hpp"

using namespace std;

class Led : public Component
{
protected:
    int led_pin;
    String event_filter;

public:
    Led(Observable *events, int led_pin);
    void setup();
    void setup(String event_filter);
    void loop();
    void notify(String event, String data);
};

#endif
