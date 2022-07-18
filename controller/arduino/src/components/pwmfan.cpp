#include "pwmfan.hpp"

#define PULSES_PER_REVOLUTION 2

PWMFan::PWMFan(
    Observable *events,
    int update_interval,
    int sense_pin,
    int pwm_pin,
    const String &channel)
    : TimedComponent(events, update_interval)
{
    this->sense_pin = sense_pin;
    this->pwm_pin = pwm_pin;
    this->channel = channel;
    this->fan_pulses = 0;
}

void PWMFan::setup()
{
    pinMode(sense_pin, INPUT_PULLUP);
    pinMode(pwm_pin, OUTPUT);
    digitalWrite(pwm_pin, HIGH);

    events->register_observer(this);
}

void PWMFan::notify(const String &event, const String &data)
{
    if (event.equals(channel + "-output"))
    {
        int value = data.toInt();
        if (value >= 0 && value <= 255)
        {
            analogWrite(pwm_pin, value);
        }
    }
}

void PWMFan::update()
{
    int pulses = fan_pulses;
    fan_pulses = 0;

    int elapsed_seconds = time_elapsed / 1000;
    int pulses_per_minute = pulses / elapsed_seconds * 60;
    int rpm = pulses_per_minute / PULSES_PER_REVOLUTION;
    events->notify_observers(channel + "-speed", String(rpm));
}

void PWMFan::pickPulse()
{
    fan_pulses++;
}
