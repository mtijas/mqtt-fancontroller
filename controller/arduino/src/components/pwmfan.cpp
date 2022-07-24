#include "pwmfan.hpp"

#define PULSES_PER_REVOLUTION 2

PWMFan::PWMFan(
    Observable *events,
    int update_interval,
    int sense_pin,
    int pwm_pin,
    const uint8_t channel)
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

    this->events->register_observer(this);
}

void PWMFan::notify(const char *event, const uint8_t channel, const char *data)
{
    if (strncmp(event, "output", 6) == 0 && channel == this->channel)
    {
        int value = atoi(data);
        if (value >= 0 && value <= 255)
        {
            analogWrite(pwm_pin, value);
        }
    }
}

void PWMFan::update()
{
    char message[6];

    int pulses = this->fan_pulses;
    this->fan_pulses = 0;

    int elapsed_seconds = time_elapsed / 1000;
    int pulses_per_minute = pulses / elapsed_seconds * 60;
    int rpm = pulses_per_minute / PULSES_PER_REVOLUTION;

    snprintf(message, sizeof message, "%i", rpm);

    this->events->notify_observers("speed", channel, message);
}

void PWMFan::pickPulse()
{
    this->fan_pulses++;
}
