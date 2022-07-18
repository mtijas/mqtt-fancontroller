/**
 * Arduino PWM fan controller
 *
 */

#include "src/utils/observable.hpp"
#include "src/components/led.hpp"
#include "src/components/momentaryled.hpp"
#include "src/modules/display.hpp"
#include "src/components/maxim18b20.hpp"

#define RST_PIN 8
#define DC_PIN 9
#define CS_PIN 10
#define BUSY_PIN 7
#define DS18B20_PIN 2

Observable events;
MomentaryLed d1(&events, 4, 50);
MomentaryLed d2(&events, 3, 50);

DS18B20 ds(DS18B20_PIN);
Maxim18b20 maxim(&events, &ds, 5000, 2);

unsigned char image[1024];
Paint paint(image, 0, 0);
Epd epd;
Epaper epaper(&paint, &epd, 200, 200);
Display display(&events, &epaper, 15000);

void setup()
{
    d1.setup("d1");
    d2.setup("d2");
    maxim.setup();
    display.setup();
}

void loop()
{
    d1.loop();
    d2.loop();
    maxim.loop();
    display.loop();

    delay(10);
}
