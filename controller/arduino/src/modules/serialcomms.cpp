#include "serialcomms.hpp"

SerialComms::SerialComms(Observable *events, int update_interval, HardwareSerial *sPort)
    : TimedComponent(events, update_interval)
{
    this->sPort = sPort;
    this->bauds = 9600;
}

void SerialComms::setup(int bauds)
{
    this->bauds = bauds;
    sPort->begin(bauds);
    lock = false;
}

void SerialComms::setup()
{
    setup(9600);
}

void SerialComms::notify(const char *event, const uint8_t channel, const char *data) {}

void SerialComms::update()
{
    if (lock || sPort->available() == 0)
    {
        return;
    }

    lock = true;

    uint8_t cmd = readUInt8();
    if (cmd != HELLO)
    {
        error();
        return;
    }
    writeCommand(ACK);

    cmd = readUInt8();
    if (cmd < SET_TARGET || cmd > GET_SETTINGS)
    {
        error();
        return;
    }
    writeCommand(RCVD);

    waitForData(1);
    char channel = readUInt8();
    if (channel < 1 || channel > 2)
    {
        error();
        return;
    }
    writeCommand(RCVD);

    switch (cmd)
    {
    case SET_TARGET:
        readTarget(channel);
        break;

    case SET_OUTPUT:
        readPidout(channel);
        break;

    case SET_KP:
        readKp(channel);
        break;

    case SET_KI:
        readKi(channel);
        break;

    case SET_KD:
        readKd(channel);
        break;

    case SET_MODE:
        readMode(channel);
        break;

    default:
        break;
    }

    lock = false;
}

void SerialComms::writeCommand(uint8_t aCommand)
{
    sPort->write(aCommand);
}

void SerialComms::waitForData(int num_bytes)
{
    unsigned long start = millis();
    while ((sPort->available() < num_bytes) && (millis() - start < 4000))
    {
    }
}

void SerialComms::readTarget(const uint8_t channel)
{
    uint16_t data = readUInt16();
    sPort->write(RCVD);

    double target = data / 100.0;

    char message[16];
    dtostrf(target, 1, 1, message);

    events->notify_observers("target", channel, message);
}

void SerialComms::readPidout(const uint8_t channel)
{
    uint8_t data = readUInt8();
    if (data < 0 || data > 255)
    {
        error();
        return;
    }
    sPort->write(RCVD);

    char message[16];
    snprintf(message, 16, "%i", data);

    events->notify_observers("output", channel, message);
}

void SerialComms::readKp(const uint8_t channel)
{
    uint16_t data = readUInt16();
    if (data < 0 || data > 65535)
    {
        error();
        return;
    }
    sPort->write(RCVD);

    double Kp = data / 100.0;

    char message[16];
    dtostrf(Kp, 1, 2, message);

    events->notify_observers("kp", channel, message);
}
void SerialComms::readKi(const uint8_t channel)
{
    uint16_t data = readUInt16();
    if (data < 0 || data > 65535)
    {
        error();
        return;
    }
    sPort->write(RCVD);

    double Ki = data / 100.0;

    char message[16];
    dtostrf(Ki, 1, 2, message);

    events->notify_observers("ki", channel, message);
}
void SerialComms::readKd(const uint8_t channel)
{
    uint16_t data = readUInt16();
    if (data < 0 || data > 65535)
    {
        error();
        return;
    }
    sPort->write(RCVD);

    double Kd = data / 100.0;

    char message[16];
    dtostrf(Kd, 1, 2, message);

    events->notify_observers("kd", channel, message);
}
void SerialComms::readMode(const uint8_t channel)
{
    uint8_t data = readUInt8();
    if (data < 0 || data > 1)
    {
        error();
        return;
    }
    sPort->write(RCVD);

    char message[16];
    snprintf(message, 16, "%i", data);

    events->notify_observers("mode", channel, message);
}

uint8_t SerialComms::readUInt8()
{
    unsigned char buf[1] = "";
    waitForData(1);
    sPort->readBytes(buf, 1);
    return buf[0];
}

uint16_t SerialComms::readUInt16()
{
    unsigned char buf[2] = "";
    waitForData(2);
    sPort->readBytes(buf, 2);
    return buf[1] << 8 | buf[0];
}

void SerialComms::error()
{
    writeCommand(ERROR);
    sPort->end();
    sPort->begin(bauds);
    lock = false;
}
