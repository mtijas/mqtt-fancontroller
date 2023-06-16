/**
 * Arduino PWM fan controller
 *
 */

#include "src/utils/observable.hpp"
#include "src/maxim18b20/maxim18b20.hpp"
#include "src/pwmfan/pwmfan.hpp"
#include "src/pidcontrol/pidcontrol.hpp"
#include "src/serialcomms/serialcomms.hpp"
#include "src/hmi/hd44780.hpp"
#include "src/hmi/alarmled.hpp"
#include "src/hmi/analogbutton.hpp"

#define DS18B20_PIN 4
#define SERIAL_RX_PIN 6
#define SERIAL_TX_PIN 7
#define FAN_SENSE_PIN 2
#define FAN_PWM_PIN 3
#define RS_PIN 12
#define EN_PIN 13
#define D4_PIN 8
#define D5_PIN 9
#define D6_PIN 10
#define D7_PIN 11
#define ALM_LED 5
#define ANALOGBTN_1_PIN A0
#define ANALOGBTN_2_PIN A1
#define ANALOGBTN_3_PIN A2

#define SERIAL_COMMS_INTERVAL 10
#define PID_CALC_INTERVAL 1000
#define FAN_SPEED_INTERVAL 2500
#define TEMP_READ_INTERVAL 1000
#define DISPLAY_UPDATE_INTERVAL 100
#define BUTTON_READ_INTERVAL 10

#define SERIAL_BAUDS 9600

Observable events;

SerialComms serialcomms(&events, SERIAL_COMMS_INTERVAL, SERIAL_RX_PIN, SERIAL_TX_PIN);

double pid_input, pid_output, pid_setpoint;
PID pid(&pid_input, &pid_output, &pid_setpoint, 0, 0, 0, REVERSE);
PIDControl pidcontroller(
    &events,
    &pid,
    PID_CALC_INTERVAL,
    &pid_input,
    &pid_output,
    &pid_setpoint);

PWMFan fan1(&events, FAN_SPEED_INTERVAL, FAN_SENSE_PIN, FAN_PWM_PIN);

DS18B20 ds(DS18B20_PIN);
Maxim18b20 maxim(&events, &ds, TEMP_READ_INTERVAL, DS18B20_PIN);

HD44780 display(&events, DISPLAY_UPDATE_INTERVAL, RS_PIN, EN_PIN, D4_PIN, D5_PIN, D6_PIN, D7_PIN);

AlarmLED alarmled(&events, ALM_LED);

AnalogButton analogbutton1(&events, BUTTON_READ_INTERVAL, ANALOGBTN_1_PIN, 1, 2);
AnalogButton analogbutton2(&events, BUTTON_READ_INTERVAL, ANALOGBTN_2_PIN, 3, 4);
AnalogButton analogbutton3(&events, BUTTON_READ_INTERVAL, ANALOGBTN_3_PIN, 5, 6);

void setup()
{
    alarmled.setup();
    display.setup();

    maxim.setup();
    fan1.setup();
    attachInterrupt(digitalPinToInterrupt(FAN_SENSE_PIN), pickFan1Pulse, FALLING);

    pidcontroller.setup();

    serialcomms.setup(SERIAL_BAUDS);

    analogbutton1.setup();
    analogbutton2.setup();
    analogbutton3.setup();

    // Notification payload is always uint16_t
    events.notify_observers("temp", 0);
    events.notify_observers("target", 0);
    events.notify_observers("speed", 0);
    events.notify_observers("output", 255);
    events.notify_observers("mode", 1);
    events.notify_observers("kp", 400); // 4.00
    events.notify_observers("ki", 40);  // 0.40
    events.notify_observers("kd", 200); // 2.00

    events.notify_observers("bootup_complete", 1);
}

void loop()
{
    fan1.loop();
    maxim.loop();
    pidcontroller.loop();
    serialcomms.loop();
    display.loop();
    analogbutton1.loop();
    analogbutton2.loop();
    analogbutton3.loop();
}

void pickFan1Pulse()
{
    fan1.pickPulse();
}
