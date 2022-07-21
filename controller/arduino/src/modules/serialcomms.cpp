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

void SerialComms::notify(const String &event, const String &data) {}

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
    uint8_t channel = readUInt8();
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

void SerialComms::readTarget(uint8_t channel)
{
    uint16_t data = readUInt16();
    sPort->write(RCVD);

    double target = data / 100.0;
    events->notify_observers("ch" + String(channel) + "-target", String(target));
}

void SerialComms::readPidout(uint8_t channel)
{
    uint8_t data = readUInt8();
    if (data < 0 || data > 255)
    {
        error();
        return;
    }
    sPort->write(RCVD);

    events->notify_observers("ch" + String(channel) + "-output", String(data));
}

void SerialComms::readKp(uint8_t channel)
{
    uint16_t data = readUInt16();
    if (data < 0 || data > 65535)
    {
        error();
        return;
    }
    sPort->write(RCVD);

    double Kp = data / 100.0;
    events->notify_observers("ch" + String(channel) + "-kp", String(Kp));
}

void SerialComms::readKi(uint8_t channel)
{
    uint16_t data = readUInt16();
    if (data < 0 || data > 65535)
    {
        error();
        return;
    }
    sPort->write(RCVD);

    double Ki = data / 100.0;
    events->notify_observers("ch" + String(channel) + "-ki", String(Ki));
}

void SerialComms::readKd(uint8_t channel)
{
    uint16_t data = readUInt16();
    if (data < 0 || data > 65535)
    {
        error();
        return;
    }
    sPort->write(RCVD);

    double Kd = data / 100.0;
    events->notify_observers("ch" + String(channel) + "-kd", String(Kd));
}

void SerialComms::readMode(uint8_t channel)
{
    uint8_t data = readUInt8();
    if (data < 0 || data > 1)
    {
        error();
        return;
    }
    sPort->write(RCVD);

    events->notify_observers("ch" + String(channel) + "-mode", String(data));
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
