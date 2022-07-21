#include "pidcontrolcomponent.hpp"

PIDControlComponent::PIDControlComponent(
    Observable *events,
    PID *pid,
    int update_interval,
    const uint8_t channel,
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

void PIDControlComponent::notify(const char *event, const uint8_t channel, const char *data)
{
    if (strncmp(event, "temp", 4) == 0 && channel == this->channel)
    {
        *input = atof(data);
    }
    else if (strncmp(event, "target", 6) == 0 && channel == this->channel)
    {
        *setpoint = atof(data);
    }
    else if (strncmp(event, "kp", 2) == 0 && channel == this->channel)
    {
        Kp = atof(data);
        pid->SetTunings(Kp, Ki, Kd);
    }
    else if (strncmp(event, "ki", 2) == 0 && channel == this->channel)
    {
        Ki = atof(data);
        pid->SetTunings(Kp, Ki, Kd);
    }
    else if (strncmp(event, "kd", 2) == 0 && channel == this->channel)
    {
        Kd = atof(data);
        pid->SetTunings(Kp, Ki, Kd);
    }
    else if (strncmp(event, "mode", 4) == 0 && channel == this->channel)
    {
        if (strncmp(data, "0", 1) == 0)
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
    char message[6];

    pid->Compute();
    if (automatic)
    {
        dtostrf(*output, 1, 1, message);

        events->notify_observers("output", channel, message);
    }
}
