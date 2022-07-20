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

    waitForData(1);
    int cmd = int(sPort->read());
    if (cmd != HELLO)
    {
        error();
        lock = false;
        return;
    }
    writeCommand(ACK);

    waitForData(1);
    cmd = int(sPort->read());
    if (cmd == -1 || cmd == ERROR) {
        error();
        lock = false;
        return;
    }
    writeCommand(RCVD);

    waitForData(1);
    int channel = int(sPort->read());
    if (channel < 1 || channel > 2) {
        error();
        lock = false;
        return;
    }
    writeCommand(RCVD);

    switch (cmd)
    {
    case TARGET:
        readTarget(channel);
        break;

    default:
        break;
    }

    lock = false;
}

void SerialComms::writeCommand(int aCommand) {
    sPort->write(aCommand);
}

void SerialComms::waitForData(int num_bytes)
{
    unsigned long start = millis();
    while ((sPort->available() < num_bytes) && (millis() - start < 4000))
    {
    }
}

void SerialComms::readTarget(int8_t channel) {
    uint16_t data = readUInt16();
    sPort->write(RCVD);

    double target = data / 100.0;
    events->notify_observers("ch" + String(channel) + "-target", String(target));
}

uint16_t SerialComms::readUInt16() {
    unsigned char buf[2] = "";
    waitForData(2);
    sPort->readBytes(buf, 2);
    return buf[0] << 8 | buf[1];
}

void SerialComms::error() {
    writeCommand(ERROR);
    sPort->end();
    sPort->begin(bauds);
}
