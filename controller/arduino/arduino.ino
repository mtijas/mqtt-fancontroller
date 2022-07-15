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

unsigned char image[1024];
Paint paint(image, 0, 0);
Epd epd;
Epaper ep_display(&events, 10000, &epd, &paint);

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
