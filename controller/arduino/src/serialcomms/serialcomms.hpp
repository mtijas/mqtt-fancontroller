#ifndef SERIALCOMMS_H
#define SERIALCOMMS_H

#include "../utils/timedcomponent.hpp"
#include <SoftwareSerial.h>

using namespace std;

enum CC {
    NUL = 0x0,
    ACK = 0x06,
    BEL = 0x07,
    LF = 0x0A,
    NAK = 0x15,
};

class SerialComms : public TimedComponent {
  protected:
    SoftwareSerial *sPort;
    int bauds, temp;
    int target, kp, ki, kd;
    int speed, output, mode, alarm;
    bool alm_fail_fan = false;
    bool alm_high_temp = false;
    bool alm_fail_sensor = false;
    volatile char message_buffer[64];
    volatile int message_length = 0;

  public:
    SerialComms(Observable *events, int update_interval, const byte rxPin,
                const byte txPin);
    void setup(int bauds);
    void setup();
    void notify(const char *event, int payload);
    void update();
    void send_data(const char *data);
    void handle_message();
};

#endif
