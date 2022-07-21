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
    GET_DATA = 70,
    GET_SETTINGS = 71
};

typedef enum Command Command;

class SerialComms
    : public TimedComponent
{
protected:
    HardwareSerial *sPort;
    bool lock;
    int bauds;
    void writeCommand(uint8_t aCommand);
    void waitForData(int num_bytes);
    void readTarget(uint8_t channel);
    void readKp(uint8_t channel);
    void readKi(uint8_t channel);
    void readKd(uint8_t channel);
    void readMode(uint8_t channel);
    void readPidout(uint8_t channel);
    void error();
    uint8_t readUInt8();
    uint16_t readUInt16();

public:
    SerialComms(Observable *events, int update_interval, HardwareSerial *sPort);
    void setup(int bauds);
    void setup();
    void notify(const String &event, const String &data);
    void update();
};

#endif
