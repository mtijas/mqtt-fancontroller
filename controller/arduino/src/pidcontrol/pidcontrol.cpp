#include "pidcontrol.hpp"

PIDControl::PIDControl(IObservable *events, PID *pid, int update_interval,
                       double *input, double *output, double *setpoint)
    : TimedComponent(events, update_interval) {
    this->pid = pid;
    this->setpoint = setpoint;
    this->input = input;
    this->output = output;
    this->automatic = true;
    this->previous_input_timestamp = 0;
    this->notemp = false;
}

void PIDControl::setup() {
    this->Kp = this->pid->GetKp();
    this->Ki = this->pid->GetKi();
    this->Kd = this->pid->GetKd();
    this->pid->SetOutputLimits(0, 255);
    this->pid->SetMode(AUTOMATIC);

    this->events->register_observer(this);
}

void PIDControl::notify(const char *event, int payload) {
    if (strncmp(event, "temp", 4) == 0) {
        *this->input = (double)payload / 10.0;
        this->previous_input_timestamp = millis();
    } else if (strncmp(event, "target", 6) == 0) {
        *this->setpoint = (double)payload / 10.0;
    } else if (strncmp(event, "kp", 2) == 0) {
        this->Kp = (double)payload / 100.0;
        this->pid->SetTunings(this->Kp, this->Ki, this->Kd);
    } else if (strncmp(event, "ki", 2) == 0) {
        this->Ki = (double)payload / 100.0;
        this->pid->SetTunings(this->Kp, this->Ki, this->Kd);
    } else if (strncmp(event, "kd", 2) == 0) {
        this->Kd = (double)payload / 100.0;
        this->pid->SetTunings(this->Kp, this->Ki, this->Kd);
    } else if (strncmp(event, "mode", 4) == 0) {
        if (payload == 0) {
            this->automatic = false;
            this->pid->SetMode(0);
        } else {
            this->automatic = true;
            this->pid->SetMode(1);
        }
    }
}

void PIDControl::update() {
    this->pid->Compute();

    if (millis() - this->previous_input_timestamp > 10000) {
        // Not receiving temperature measurements
        if (!this->notemp) {
            this->events->notify_observers("alm_fail_sensor", 1);
            this->notemp = true;
        }
    } else {
        if (this->notemp) {
            this->events->notify_observers("alm_fail_sensor", 0);
            this->notemp = false;
        }
    }

    if (automatic) {
        this->events->notify_observers("output", (int)*this->output);
    }
}
