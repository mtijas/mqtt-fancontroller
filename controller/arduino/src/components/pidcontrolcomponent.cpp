#include "pidcontrolcomponent.hpp"

PIDControlComponent::PIDControlComponent(
    Observable *events,
    PID *pid,
    int update_interval,
    const String &channel,
    double *input,
    double *output,
    double *setpoint)
    : TimedComponent(events, update_interval)
{
    this->pid = pid;
    this->channel = channel;
    this->setpoint = setpoint;
    this->input = input;
    this->output = output;
    this->automatic = true;
}

void PIDControlComponent::setup()
{
    Kp = pid->GetKp();
    Ki = pid->GetKi();
    Kd = pid->GetKd();
    pid->SetOutputLimits(0, 255);
    pid->SetMode(AUTOMATIC);

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
    else if (event.equals(channel + "-kp"))
    {
        Kp = data.toDouble();
        pid->SetTunings(Kp, Ki, Kd);
    }
    else if (event.equals(channel + "-ki"))
    {
        Ki = data.toDouble();
        pid->SetTunings(Kp, Ki, Kd);
    }
    else if (event.equals(channel + "-kd"))
    {
        Kd = data.toDouble();
        pid->SetTunings(Kp, Ki, Kd);
    }
    else if (event.equals(channel + "-mode"))
    {
        if (data.equals("0"))
        {
            automatic = false;
            pid->SetMode(0);
        }
        else
        {
            automatic = true;
            pid->SetMode(1);
        }
    }
}

void PIDControlComponent::update()
{
    pid->Compute();
    if (automatic)
    {
        events->notify_observers(channel + "-output", String(*output));
    }
}
