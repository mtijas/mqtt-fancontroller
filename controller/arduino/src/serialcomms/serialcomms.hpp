#ifndef SERIALCOMMS_H
#define SERIALCOMMS_H

#include "../utils/timedcomponent.hpp"
#include <SoftwareSerial.h>

using namespace std;

enum CC {
    NUL = 0x0,
    ACK = 0x06,
    BEL = 0x07,
    BS = 0x08,
    LF = 0x0A,
    CR = 0x0D,
    NAK = 0x15,
    DEL = 0x7F,
};

class SerialComms : public TimedComponent {
  protected:
    SoftwareSerial *sPort;
    int bauds, temp;
    int target, kp, ki, kd;
    int speed, output, mode, alarm;
    const int ASCII_PRINTABLE_LOWER_LIMIT = 0x20;
    const int ASCII_PRINTABLE_UPPER_LIMIT = 0x7E;
    bool alm_fail_fan = false;
    bool alm_high_temp = false;
    bool alm_fail_sensor = false;
    volatile char message_buffer[64];
    volatile int message_length = 0;

    void show_help();

  public:
    SerialComms(IObservable *events, int update_interval, const byte rxPin,
                const byte txPin);
    void setup(int bauds);
    void setup();
    void notify(const char *event, int payload);
    void update();
    void send_data(const char *data);
    void handle_message();
};

#endif
