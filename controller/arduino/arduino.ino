/**
 * Arduino PWM fan controller
 *
 */

#include "src/utils/observable.hpp"
#include "src/modules/led.hpp"
#include "src/modules/momentaryled.hpp"
#include "src/modules/epaper.hpp"

Observable events;
MomentaryLed d1(&events, 4, 100);
MomentaryLed d2(&events, 3, 100);
Epaper ep_display(&events, 1000);

void setup()
{
    d1.setup("d1");
    d2.setup("d2");
    ep_display.setup();
}

void loop()
{
    d1.loop();
    d2.loop();
    ep_display.loop();

    delay(100);
}
