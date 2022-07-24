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
    this->previous_input_timestamp = 0;
    this->notemp = false;
}

void PIDControlComponent::setup()
{
    this->Kp = pid->GetKp();
    this->Ki = pid->GetKi();
    this->Kd = pid->GetKd();
    this->pid->SetOutputLimits(0, 255);
    this->pid->SetMode(AUTOMATIC);

    this->events->register_observer(this);
}

void PIDControlComponent::notify(const char *event, const uint8_t channel, const char *data)
{
    if (strncmp(event, "temp", 4) == 0 && channel == this->channel)
    {
        *input = atof(data);
        this->previous_input_timestamp = millis();
    }
    else if (strncmp(event, "target", 6) == 0 && channel == this->channel)
    {
        *setpoint = atof(data);
    }
    else if (strncmp(event, "kp", 2) == 0 && channel == this->channel)
    {
        this->Kp = atof(data);
        this->pid->SetTunings(this->Kp, this->Ki, this->Kd);
    }
    else if (strncmp(event, "ki", 2) == 0 && channel == this->channel)
    {
        this->Ki = atof(data);
        this->pid->SetTunings(this->Kp, this->Ki, this->Kd);
    }
    else if (strncmp(event, "kd", 2) == 0 && channel == this->channel)
    {
        this->Kd = atof(data);
        this->pid->SetTunings(this->Kp, this->Ki, this->Kd);
    }
    else if (strncmp(event, "mode", 4) == 0 && channel == this->channel)
    {
        if (strncmp(data, "0", 1) == 0)
        {
            this->automatic = false;
            this->pid->SetMode(0);
        }
        else
        {
            this->automatic = true;
            this->pid->SetMode(1);
        }
    }
}

void PIDControlComponent::update()
{
    char message[6];

    this->pid->Compute();
    if (automatic)
    {
        dtostrf(*output, 1, 1, message);
        if (millis() - this->previous_input_timestamp > 30000)
        {
            // Not receiving temperature measurements
            this->events->notify_observers("output", channel, "255");
            if (!this->notemp)
            {
                this->events->notify_observers("mode", channel, "2");
                this->notemp = true;
            }
        }
        else
        {
            this->events->notify_observers("output", channel, message);
            if (this->notemp)
            {
                this->events->notify_observers("mode", channel, "1");
                this->notemp = false;
            }
        }
    }
}
