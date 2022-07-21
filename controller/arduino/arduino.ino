/**
 * Arduino PWM fan controller
 *
 */

#include "src/utils/observable.hpp"
#include "src/modules/display.hpp"
#include "src/components/maxim18b20.hpp"
#include "src/components/pwmfan.hpp"
#include "src/components/pidcontrolcomponent.hpp"
#include "src/modules/serialcomms.hpp"

#define RST_PIN 8
#define DC_PIN 9
#define CS_PIN 10
#define BUSY_PIN 7
#define DS18B20_PIN 2

Observable events;

SerialComms serialcomms(&events, 1000, &Serial);

double pid1_input, pid1_output, pid1_setpoint;
PID pid1(&pid1_input, &pid1_output, &pid1_setpoint, 5.0, 0.2, 1.0, REVERSE);
PIDControlComponent pc1(
    &events,
    &pid1,
    1000,
    "ch1",
    &pid1_input,
    &pid1_output,
    &pid1_setpoint);

double pid2_input, pid2_output, pid2_setpoint;
PID pid2(&pid2_input, &pid2_output, &pid2_setpoint, 5.0, 0.2, 1.0, REVERSE);
PIDControlComponent pc2(
    &events,
    &pid2,
    1000,
    "ch2",
    &pid2_input,
    &pid2_output,
    &pid2_setpoint);

PWMFan fan1(&events, 3000, 3, 5, "ch1");
PWMFan fan2(&events, 3000, 4, 6, "ch2");

DS18B20 ds(DS18B20_PIN);
Maxim18b20 maxim(&events, &ds, 5000, 2);

unsigned char image[512];
Paint paint(image, 0, 0);
Epd epd;
Epaper epaper(&paint, &epd, 200, 200);
Display display(&events, &epaper, 15000);

void setup()
{
    Serial.begin(9600);
    display.setup();
    maxim.setup();
    fan1.setup();
    attachInterrupt(digitalPinToInterrupt(3), pickFan1Pulse, FALLING);

    fan2.setup();
    attachInterrupt(digitalPinToInterrupt(4), pickFan2Pulse, FALLING);

    pc1.setup();
    pc2.setup();

    serialcomms.setup(9600);

    events.notify_observers("ch1-temp", "--.--");
    events.notify_observers("ch2-temp", "--.--");
    events.notify_observers("ch1-target", "30.00");
    events.notify_observers("ch2-target", "30.00");
    events.notify_observers("ch1-speed", "----");
    events.notify_observers("ch2-speed", "----");
    events.notify_observers("ch1-output", "255");
    events.notify_observers("ch2-output", "255");
    events.notify_observers("ch1-mode", "1");
    events.notify_observers("ch2-mode", "1");
}

void loop()
{
    fan1.loop();
    fan2.loop();
    maxim.loop();
    pc1.loop();
    pc2.loop();
    serialcomms.loop();
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
