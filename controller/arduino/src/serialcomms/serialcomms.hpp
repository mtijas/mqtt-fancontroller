#ifndef SERIALCOMMS_H
#define SERIALCOMMS_H

#include <SoftwareSerial.h>
#include <CRC16.h>
#include "../utils/timedcomponent.hpp"

using namespace std;

enum CC
{
    NUL = 0x0,
    SOH = 0x01,
    STX = 0x02,
    ETX = 0x03,
    EOT = 0x04,
    ENQ = 0x05,
    ACK = 0x06,
    BEL = 0x07,
    NAK = 0x08,
    READ_TEMP = 0x21,
    READ_TARGET = 0x22,
    READ_SPEED = 0x23,
    READ_PWM = 0x24,
    READ_KP = 0x25,
    READ_KI = 0x26,
    READ_KD = 0x27,
    READ_MODE = 0x28,
    READ_ALARM = 0x29,
    WRITE_TEMP = 0x31,
    WRITE_TARGET = 0x32,
    WRITE_SPEED = 0x33,
    WRITE_PWM = 0x34,
    WRITE_KP = 0x35,
    WRITE_KI = 0x36,
    WRITE_KD = 0x37,
    WRITE_MODE = 0x38,
    WRITE_ALARM = 0x39,
};

class SerialComms
    : public TimedComponent
{
protected:
    SoftwareSerial *sPort;
    int bauds;
    char temp[8], target[8], kp[7], ki[7], kd[7];
    char speed[5], output[4], mode[2], alarm[2];
    volatile char message_buffer[17];
    volatile int message_length = 0;
    CRC16 *crc;

public:
    SerialComms(Observable *events, int update_interval, const byte rxPin, const byte txPin);
    void setup(int bauds);
    void setup();
    void notify(const char *event, uint16_t payload);
    void update();
    void send_data(char command, const char *data);
    bool validate_message();
    void handle_message();
};

#endif
