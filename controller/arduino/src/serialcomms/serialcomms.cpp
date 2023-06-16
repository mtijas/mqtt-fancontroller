#include "serialcomms.hpp"

SerialComms::SerialComms(
    Observable *events,
    int update_interval,
    const byte rxPin,
    const byte txPin) : TimedComponent(events, update_interval)
{
    this->sPort = new SoftwareSerial(rxPin, txPin);
    this->bauds = 9600;
}

void SerialComms::setup(int bauds)
{
    this->crc = new CRC16(0x1021, 0xFFFF, 0, false, false);
    this->bauds = bauds;
    sPort->begin(bauds);
    sPort->listen();
    events->register_observer(this);
}

void SerialComms::setup()
{
    setup(9600);
}

void SerialComms::notify(const char *event, uint16_t payload)
{
    float temporary = 0.0;

    if (strncmp(event, "temp", 4) == 0)
    {
        dtostrf(payload, 1, 0, temp);
    }
    else if (strncmp(event, "target", 6) == 0)
    {
        dtostrf(payload, 1, 0, target);
    }
    else if (strncmp(event, "speed", 5) == 0)
    {
        dtostrf(payload, 1, 0, speed);
    }
    else if (strncmp(event, "output", 6) == 0)
    {
        dtostrf(payload, 1, 0, output);
    }
    else if (strncmp(event, "mode", 4) == 0)
    {
        dtostrf(payload, 1, 0, mode);
    }
    else if (strncmp(event, "kp", 2) == 0)
    {
        dtostrf(payload, 1, 0, kp);
    }
    else if (strncmp(event, "ki", 2) == 0)
    {
        dtostrf(payload, 1, 0, ki);
    }
    else if (strncmp(event, "kd", 2) == 0)
    {
        dtostrf(payload, 1, 0, kd);
    }
    else if (strncmp(event, "alarm", 5) == 0)
    {
        dtostrf(payload, 1, 0, alarm);
    }
    else if (strncmp(event, "keypress", 8) == 0)
    {
        sPort->print(payload);
    }
}

void SerialComms::update()
{
    char received;
    if (sPort->available())
    {
        received = sPort->read();
        if (received == STX)
        {
            // Start of TeXt: discard any old data
            message_buffer[0] = '\n';
            message_length = 0;
        }
        else if (received == ETX)
        {
            // End of TeXt: maybe we received a whole message
            // Let's check that by validating message CRC
            if (validate_message())
            {
                handle_message();
            }
            else
            {
                sPort->write(NAK);
            }
            // Message handled in some way. Discard the message.
            message_buffer[0] = '\n';
            message_length = 0;
        }
        else
        {
            // Received byte wasn't a known control character, so
            // let's assume it is part of the message body.
            // We also assume message length to never exceed 16 chars total.
            // Message validation depends on capping the length to 16!
            if (message_length < 16)
            {
                message_buffer[message_length] = received;
                message_length++;
                message_buffer[message_length] = '\n';
            }
            else
            {
                // Input message buffer full. Indicate that by NAKing
                // every received char until known control char is
                // received. Not a good solution but at least we don't
                // ghost the sender completely.
                sPort->write(NAK);
            }
        }
    }
}

void SerialComms::send_data(char command, const char *data)
{
    char *ptr = data;
    char crc_str[5];
    uint16_t crc_result = 0x0;

    crc->restart();

    sPort->write(STX);
    sPort->write(command);
    crc->add(command);

    ptr = data;
    for (char c = *ptr; c; c = *++ptr)
    {
        sPort->write(c);
        crc->add(c);
    }

    crc_result = crc->getCRC();
    snprintf(crc_str, 5, "%04x", crc_result);
    sPort->print(crc_str);
    sPort->write(ETX);
}

bool SerialComms::validate_message()
{
    // A valid message should always consist of at least one data
    // char and four chars of CRC.
    if (message_length < 5)
    {
        return false;
    }

    // CRC16 should be the last four ascii chars of the message
    char crc_str[5];
    crc_str[0] = message_buffer[message_length - 4];
    crc_str[1] = message_buffer[message_length - 3];
    crc_str[2] = message_buffer[message_length - 2];
    crc_str[3] = message_buffer[message_length - 1];
    crc_str[4] = '\n';

    // Convert the ascii representation into a proper 16-bit int
    uint16_t crc_value;
    if (sscanf(crc_str, "%X", &crc_value) != 1)
    {
        return false;
    }

    crc->restart(); // We use the same CRC object for sending as well...

    char payload[13]; // Payload is anything but CRC, assume 12 chars max.
    for (int i = 0; i < message_length - 4; i++)
    {
        payload[i] = message_buffer[i];
        crc->add(message_buffer[i]);
    }

    uint16_t calculated_crc = crc->getCRC();

    if (calculated_crc == crc_value)
    {
        return true;
    }
    return false;
}

void SerialComms::handle_message()
{
    char message[12];

    // Command character should always be the first char of message body
    char command = message_buffer[0];

    // Payload is anything but command and CRC, assume 11 chars max.
    char payload[12];
    for (int i = 1; i < message_length - 4; i++)
    {
        payload[i - 1] = message_buffer[i];
        payload[i] = '\n';
    }

    switch (command)
    {
    case READ_TEMP:
        sPort->write(ACK);
        snprintf(message, 12, "%s", temp);
        send_data(WRITE_TEMP, message);
        break;
    case READ_TARGET:
        sPort->write(ACK);
        snprintf(message, 12, "%s", target);
        send_data(WRITE_TARGET, message);
        break;
    case READ_SPEED:
        sPort->write(ACK);
        snprintf(message, 12, "%s", speed);
        send_data(WRITE_SPEED, message);
        break;
    case READ_PWM:
        sPort->write(ACK);
        snprintf(message, 4, "%s", output);
        send_data(WRITE_PWM, message);
        break;
    case READ_KP:
        sPort->write(ACK);
        snprintf(message, 12, "%s", kp);
        send_data(WRITE_KP, message);
        break;
    case READ_KI:
        sPort->write(ACK);
        snprintf(message, 12, "%s", ki);
        send_data(WRITE_KI, message);
        break;
    case READ_KD:
        sPort->write(ACK);
        snprintf(message, 12, "%s", kd);
        send_data(WRITE_KD, message);
        break;
    case READ_MODE:
        sPort->write(ACK);
        snprintf(message, 2, "%s", mode);
        send_data(WRITE_MODE, message);
        break;
    case READ_ALARM:
        sPort->write(ACK);
        snprintf(message, 12, "%s", alarm);
        send_data(WRITE_ALARM, message);
        break;
    case WRITE_TARGET:
        sPort->write(ACK);
        events->notify_observers("target", atoi(payload));
        break;
    default:
        sPort->write(NAK);
    }
}
