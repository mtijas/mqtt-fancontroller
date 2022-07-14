/**
 * Arduino PWM fan controller
 *
 */

#include "src/utils/observable.hpp"
#include "src/modules/led.hpp"
#include "src/modules/momentaryled.hpp"

int alm_counter = 0;
bool alm_on = false;
Observable events;
Led alarm_led(&events, 4);
MomentaryLed data_led(&events, 3, 100);

void setup()
{
    alarm_led.setup("alarm");
    data_led.setup("serial-data-received");
}

void loop()
{
    if (alm_counter % 50 == 0)
    {
        events.notify_observers("serial-data-received", "on");
    }

    alm_counter++;
    if (alm_counter > 100)
    {
        if (!alm_on)
        {
            events.notify_observers("alarm", "on");
        }
        else
        {
            events.notify_observers("alarm", "off");
        }
        alm_on = !alm_on;
        alm_counter = 0;
    }

    alarm_led.loop();
    data_led.loop();

    delay(10);
}
