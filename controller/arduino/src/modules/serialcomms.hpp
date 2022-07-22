#ifndef SERIALCOMMS_H
#define SERIALCOMMS_H

#include "Arduino.h"
#include "../utils/timedcomponent.hpp"

using namespace std;

enum Command
{
    HELLO = 1,
    ACK = 2,
    RCVD = 3,
    END = 6,
    ERROR = 7,
    SET_TARGET = 64,
    SET_OUTPUT = 65,
    SET_KP = 66,
    SET_KI = 67,
    SET_KD = 68,
    SET_MODE = 69,
    GET_STATUS = 70, //Status report request
    GET_SETTINGS = 71, //Settings report request
};

typedef enum Command Command;

class SerialComms
    : public TimedComponent
{
protected:
    HardwareSerial *sPort;
    bool lock;
    int bauds;
    int16_t status[2][4]; //dim 1: channels, dim 2: temp, target, speed, output
    uint16_t settings[2][4]; //dim 1: channels, dim 2: mode, kp, ki, kd
    void waitForData(int num_bytes);
    void readTarget(const uint8_t channel);
    void readKp(const uint8_t channel);
    void readKi(const uint8_t channel);
    void readKd(const uint8_t channel);
    void readMode(const uint8_t channel);
    void readPidout(const uint8_t channel);
    void sendStatusReport(const uint8_t channel);
    void sendSettingsReport(const uint8_t channel);
    void error();
    uint8_t readUInt8();
    uint16_t readUInt16();
    void writeUInt16(uint16_t);
    void writeInt16(int16_t);

public:
    SerialComms(Observable *events, int update_interval, HardwareSerial *sPort);
    void setup(int bauds);
    void setup();
    void notify(const char *event, const uint8_t channel, const char *data);
    void update();
};

#endif
