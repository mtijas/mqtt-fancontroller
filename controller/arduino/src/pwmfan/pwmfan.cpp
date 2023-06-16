#include "pwmfan.hpp"

#define PULSES_PER_REVOLUTION 2.0

PWMFan::PWMFan(
    Observable *events,
    int update_interval,
    int sense_pin,
    int pwm_pin)
    : TimedComponent(events, update_interval)
{
    this->sense_pin = sense_pin;
    this->pwm_pin = pwm_pin;
    this->fan_pulses = 0;
}

void PWMFan::setup()
{
    pinMode(sense_pin, INPUT_PULLUP);
    pinMode(pwm_pin, OUTPUT);
    digitalWrite(pwm_pin, HIGH);

    this->events->register_observer(this);
}

void PWMFan::notify(const char *event, uint16_t payload)
{
    if (strncmp(event, "output", 6) == 0)
    {
        if (payload >= 0 && payload <= 255)
        {
            analogWrite(pwm_pin, payload);
        }
    }
}

void PWMFan::update()
{
    int pulses = this->fan_pulses;
    this->fan_pulses = 0;

    double elapsed_seconds = time_elapsed / 1000.0;
    double pulses_per_minute = pulses / elapsed_seconds * 60;
    int rpm = int(pulses_per_minute / PULSES_PER_REVOLUTION);

    this->events->notify_observers("speed", rpm);
    if (rpm == 0)
    {
        this->events->notify_observers("alarm", 1);
    }
    else
    {
        this->events->notify_observers("alarm", 0);
    }
}

void PWMFan::pickPulse()
{
    this->fan_pulses++;
}
