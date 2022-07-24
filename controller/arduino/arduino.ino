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
#define DS18B20_PIN 4

Observable events;

SerialComms serialcomms(&events, 1000, &Serial);

double pid1_input, pid1_output, pid1_setpoint;
PID pid1(&pid1_input, &pid1_output, &pid1_setpoint, 0, 0, 0, REVERSE);
PIDControlComponent pc1(
    &events,
    &pid1,
    1000,
    1,
    &pid1_input,
    &pid1_output,
    &pid1_setpoint);

double pid2_input, pid2_output, pid2_setpoint;
PID pid2(&pid2_input, &pid2_output, &pid2_setpoint, 0, 0, 0, REVERSE);
PIDControlComponent pc2(
    &events,
    &pid2,
    1000,
    2,
    &pid2_input,
    &pid2_output,
    &pid2_setpoint);

PWMFan fan1(&events, 3000, 2, 5, 1);
PWMFan fan2(&events, 3000, 3, 6, 2);

DS18B20 ds(DS18B20_PIN);
Maxim18b20 maxim(&events, &ds, 5000, DS18B20_PIN);

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
    attachInterrupt(digitalPinToInterrupt(2), pickFan1Pulse, FALLING);

    fan2.setup();
    attachInterrupt(digitalPinToInterrupt(3), pickFan2Pulse, FALLING);

    pc1.setup();
    pc2.setup();

    serialcomms.setup(9600);

    events.notify_observers("temp", 1, "--.-");
    events.notify_observers("temp", 2, "--.-");
    events.notify_observers("target", 1, "30.0");
    events.notify_observers("target", 2, "30.0");
    events.notify_observers("speed", 1, "----");
    events.notify_observers("speed", 2, "----");
    events.notify_observers("output", 1, "255");
    events.notify_observers("output", 2, "255");
    events.notify_observers("mode", 1, "1");
    events.notify_observers("mode", 2, "1");
    events.notify_observers("kp", 1, "4.0");
    events.notify_observers("kp", 2, "4.0");
    events.notify_observers("ki", 1, "0.4");
    events.notify_observers("ki", 2, "0.4");
    events.notify_observers("kd", 1, "2.0");
    events.notify_observers("kd", 2, "2.0");
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
