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
    events->register_observer(this);
}

void SerialComms::setup()
{
    setup(9600);
}

void SerialComms::notify(const char *event, const uint8_t channel, const char *data) {
    if (channel < 1 || channel > 2) {
        return;
    }

    if (strncmp(event, "temp", 4) == 0) {
        status[channel-1][0] = atof(data) * 10;
    }
    else if (strncmp(event, "target", 6) == 0) {
        status[channel-1][1] = atof(data) * 10;
    }
    else if (strncmp(event, "speed", 5) == 0) {
        status[channel-1][2] = atoi(data);
    }
    else if (strncmp(event, "output", 6) == 0) {
        status[channel-1][3] = atoi(data);
    }
    else if (strncmp(event, "mode", 4) == 0) {
        settings[channel-1][0] = atoi(data);
    }
    else if (strncmp(event, "kp", 2) == 0) {
        settings[channel-1][1] = atof(data) * 100;
    }
    else if (strncmp(event, "ki", 2) == 0) {
        settings[channel-1][2] = atof(data) * 100;
    }
    else if (strncmp(event, "kd", 2) == 0) {
        settings[channel-1][3] = atof(data) * 100;
    }
}

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
    sPort->write(ACK);

    waitForData(1);
    cmd = readUInt8();
    if (cmd < SET_TARGET || cmd > GET_SETTINGS)
    {
        error();
        return;
    }

    waitForData(1);
    char channel = readUInt8();
    if (channel < 1 || channel > 2)
    {
        error();
        return;
    }

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

    case GET_SETTINGS:
        sendSettingsReport(channel);
        break;

    case GET_STATUS:
        sendStatusReport(channel);
        break;

    default:
        error();
        break;
    }

    lock = false;
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

    double target = data / 10.0;

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

void SerialComms::sendSettingsReport(const uint8_t channel)
{
    writeUInt16(settings[channel-1][0]);
    writeUInt16(settings[channel-1][1]);
    writeUInt16(settings[channel-1][2]);
    writeUInt16(settings[channel-1][3]);
    waitForData(1);
    uint8_t response = readUInt8();
}

void SerialComms::sendStatusReport(const uint8_t channel)
{
    writeInt16(status[channel-1][0]);
    writeInt16(status[channel-1][1]);
    writeInt16(status[channel-1][2]);
    writeInt16(status[channel-1][3]);
    waitForData(1);
    uint8_t response = readUInt8();
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

void SerialComms::writeUInt16(uint16_t data) {
    sPort->write(data & 0xFF);
    sPort->write(data >> 8);
}

void SerialComms::writeInt16(int16_t data) {
    uint16_t unsigned_data = 32768;
    unsigned_data += data;
    sPort->write(unsigned_data & 0xFF);
    sPort->write(unsigned_data >> 8);
}

void SerialComms::error()
{
    sPort->write(ERROR);
    sPort->end();
    sPort->begin(bauds);
    lock = false;
}
