#ifndef SERIALCOMMS_H
#define SERIALCOMMS_H

#include "Arduino.h"
#include "../utils/timedcomponent.hpp"

using namespace std;

enum Command {
    HELLO = 1,
    ACK = 2,
    RCVD = 3,
    END = 6,
    ERROR = 7,
    TEMPERATURE = 64,
    TARGET = 65,
    FANSPD = 66,
    PIDOUT = 67,
    KP = 68,
    KI = 69,
    KD = 70,
    MODE = 71
};

typedef enum Command Command;

class SerialComms
    : public TimedComponent
{
private:

protected:
    HardwareSerial *sPort;
    bool lock;
    int bauds;
    void writeCommand(int aCommand);
    void waitForData(int num_bytes);
    void readTarget(int8_t channel);
    void error();
    uint16_t readUInt16();

public:
    SerialComms(Observable *events, int update_interval, HardwareSerial *sPort);
    void setup(int bauds);
    void setup();
    void notify(const String &event, const String &data);
    void update();
};

#endif
