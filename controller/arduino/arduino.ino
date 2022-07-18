/**
 * Arduino PWM fan controller
 *
 */

#include "src/utils/observable.hpp"
#include "src/modules/display.hpp"
#include "src/components/maxim18b20.hpp"
#include "src/components/pwmfan.hpp"

#define RST_PIN 8
#define DC_PIN 9
#define CS_PIN 10
#define BUSY_PIN 7
#define DS18B20_PIN 2

Observable events;

PWMFan fan1(&events, 2000, 3, 5, 1);
PWMFan fan2(&events, 2000, 4, 6, 2);

DS18B20 ds(DS18B20_PIN);
Maxim18b20 maxim(&events, &ds, 5000, 2);

unsigned char image[1024];
Paint paint(image, 0, 0);
Epd epd;
Epaper epaper(&paint, &epd, 200, 200);
Display display(&events, &epaper, 15000);

void setup()
{
    display.setup();
    maxim.setup();
    fan1.setup();
    attachInterrupt(digitalPinToInterrupt(3), pickFan1Pulse, FALLING);

    fan2.setup();
    attachInterrupt(digitalPinToInterrupt(4), pickFan2Pulse, FALLING);

    events.notify_observers("ch1-temp", "--.--");
    events.notify_observers("ch2-temp", "--.--");
    events.notify_observers("ch1-target", "30.00");
    events.notify_observers("ch2-target", "30.00");
    events.notify_observers("ch1-speed", "----");
    events.notify_observers("ch2-speed", "----");
    events.notify_observers("ch1-output", "Wait");
    events.notify_observers("ch2-output", "Wait");
}

void loop()
{
    fan1.loop();
    fan2.loop();
    maxim.loop();
    display.loop();

    delay(10);
}

void pickFan1Pulse()
{
    fan1.pickPulse();
}

void pickFan2Pulse()
{
    fan2.pickPulse();
}
