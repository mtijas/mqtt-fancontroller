#include "pidcontrolcomponent.hpp"

PIDControlComponent::PIDControlComponent(
    Observable *events,
    AutoPID *pid,
    int update_interval,
    const String &channel,
    double *input,
    double *output,
    double *setpoint,
    bool invert)
    : TimedComponent(events, update_interval)
{
    this->pid = pid;
    this->channel = channel;
    this->setpoint = setpoint;
    this->input = input;
    this->output = output;
    this->invert = invert;
}

void PIDControlComponent::setup()
{
    Kp = 1.0;
    Ki = 0.1;
    Kd = 0.5;
    pid->setOutputRange(0, 255);
    pid->setGains(Kp, Ki, Kd);
    events->register_observer(this);
}

void PIDControlComponent::notify(const String &event, const String &data)
{
    if (event.equals(channel + "-temp"))
    {
        *input = data.toDouble();
    }
    else if (event.equals(channel + "-target"))
    {
        *setpoint = data.toDouble();
    }
}

void PIDControlComponent::update()
{
    pid->run();
    if (invert) {
        events->notify_observers(channel + "-output", String(255 - *output));
    } else {
        events->notify_observers(channel + "-output", String(*output));
    }
}
