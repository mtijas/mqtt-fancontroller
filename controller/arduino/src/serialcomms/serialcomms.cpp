#include "serialcomms.hpp"

SerialComms::SerialComms(Observable *events, int update_interval,
                         const byte rxPin, const byte txPin)
    : TimedComponent(events, update_interval) {
    this->sPort = new SoftwareSerial(rxPin, txPin);
    this->bauds = 9600;
}

void SerialComms::setup(int bauds) {
    this->crc = new CRC16(0x1021, 0xFFFF, 0, false, false);
    this->bauds = bauds;
    sPort->begin(bauds);
    sPort->listen();
    send_data("MQTT Fan Contr.");
    send_data("Serial Console");
    send_data("?");
    events->register_observer(this);
}

void SerialComms::setup() { setup(9600); }

void SerialComms::notify(const char *event, int payload) {
    float temporary = 0.0;

    if (strncmp(event, "temp", 4) == 0) {
        temp = payload;
    } else if (strncmp(event, "target", 6) == 0) {
        target = payload;
    } else if (strncmp(event, "speed", 5) == 0) {
        speed = payload;
    } else if (strncmp(event, "output", 6) == 0) {
        output = payload;
    } else if (strncmp(event, "mode", 4) == 0) {
        mode = payload;
    } else if (strncmp(event, "kp", 2) == 0) {
        kp = payload;
    } else if (strncmp(event, "ki", 2) == 0) {
        ki = payload;
    } else if (strncmp(event, "kd", 2) == 0) {
        kd = payload;
    } else if (strncmp(event, "alarm", 5) == 0) {
        alarm = payload;
    } else if (strncmp(event, "keypress", 8) == 0) {
        sPort->print(payload);
    } else if (strncmp(event, "pending_write", 13) == 0) {
        send_data("Pending save!");
    } else if (strncmp(event, "alm_fail_fan", 12) == 0) {
        if (payload == 1) {
            send_data("FAN FAILED!");
            alm_fail_fan = true;
        } else {
            alm_fail_fan = false;
        }
    } else if (strncmp(event, "alm_fail_sensor", 12) == 0) {
        if (payload == 1) {
            send_data("SENSOR FAILED!");
            alm_fail_sensor = true;
        } else {
            alm_fail_sensor = false;
        }
    } else if (strncmp(event, "alm_high_temp", 12) == 0) {
        if (payload == 1) {
            send_data("HIGH TEMPERATURE!");
            alm_high_temp = true;
        } else {
            alm_high_temp = false;
        }
    }
}

void SerialComms::update() {
    char received;
    if (sPort->available()) {
        received = sPort->read();
        if (received == LF) {
            // Line Feed: maybe we received a whole message
            // Let's check that by validating message CRC
            if (validate_message()) {
                handle_message();
            } else {
                sPort->write(NAK);
            }
            // Message handled in some way. Discard the message.
            message_buffer[0] = '\n';
            message_length = 0;
        } else {
            // Received byte wasn't LF, so let's assume it is part of the message body.
            // We also assume message length to never exceed 64 chars total.
            // Message validation depends on capping the length to 64!
            if (message_length < 63) {
                message_buffer[message_length] = received;
                message_length++;
                message_buffer[message_length] = '\n';
            } else {
                // Input message buffer full. Indicate that by NAKing
                // every received char until known control char is
                // received. Not a good solution but at least we don't
                // ghost the sender completely.
                sPort->write(NAK);
            }
        }
    }
}

void SerialComms::send_data(const char *data) {
    char *ptr = data;
    char crc_str[5];
    int crc_result = 0x0;

    crc->restart();

    for (char c = *ptr; c; c = *++ptr) {
        if (c == '\n') {
            break;
        }
        sPort->write(c);
        crc->add(c);
    }

    crc_result = crc->getCRC();
    snprintf(crc_str, 5, "%04X", crc_result);
    sPort->print(crc_str);
    sPort->write(LF);
}

bool SerialComms::validate_message() {
    // A valid message should always consist of at least one data
    // char and four chars of CRC.
    if (message_length < 5) {
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
    int crc_value;
    if (sscanf(crc_str, "%X", &crc_value) != 1) {
        return false;
    }

    crc->restart(); // We use the same CRC object for sending as well...

    char payload[13]; // Payload is anything but CRC, assume 12 chars max.
    for (int i = 0; i < message_length - 4; i++) {
        payload[i] = message_buffer[i];
        crc->add(message_buffer[i]);
    }

    int calculated_crc = crc->getCRC();

    if (calculated_crc == crc_value) {
        return true;
    }
    return false;
}

void SerialComms::handle_message() {
    char message[12];
    int attr_val = -999;

    // Payload is anything but CRC, assume 32 chars max.
    char command[32];
    char attribute[32];
    command[0] = '\n';
    attribute[0] = '\n';
    int position = 0;
    int part = 0;
    for (int i = 0; i < message_length - 4; i++) {
        char chr = message_buffer[i];
        if (chr == ' ') {
            part++;
            position = 0;
        } else {
            if (part == 0) {
                command[position] = chr;
                command[position+1] = '\n';
            } else {
                attribute[position] = chr;
                attribute[position+1] = '\n';
            }
            position++;
        }
    }

    if (attribute[0] != '\n') {
        attr_val = atoi(attribute);
    }

    if (strncmp(command, "read_temp", 9) == 0) {
        snprintf(message, 12, "%d", temp);
        send_data(message);
    } else if (strncmp(command, "read_target", 11) == 0) {
        snprintf(message, 12, "%d", target);
        send_data(message);
    } else if (strncmp(command, "read_speed", 10) == 0) {
        snprintf(message, 12, "%d", speed);
        send_data(message);
    } else if (strncmp(command, "read_pwm", 8) == 0) {
        snprintf(message, 4, "%d", output);
        send_data(message);
    } else if (strncmp(command, "read_kp", 7) == 0) {
        snprintf(message, 12, "%d", kp);
        send_data(message);
    } else if (strncmp(command, "read_ki", 7) == 0) {
        snprintf(message, 12, "%d", ki);
        send_data(message);
    } else if (strncmp(command, "read_kd", 7) == 0) {
        snprintf(message, 12, "%d", kd);
        send_data(message);
    } else if (strncmp(command, "read_mode", 9) == 0) {
        snprintf(message, 2, "%d", mode);
        send_data(message);
    } else if (strncmp(command, "read_alarm", 10) == 0) {
        snprintf(message, 12, "%d", alarm);
        send_data(message);
    } else if (strncmp(command, "write_target", 12) == 0) {
        if (part > 0 && attr_val >= 0 && attr_val <= 1500) {
            sPort->write(ACK);
            events->notify_observers("target", attr_val);
        } else {
            sPort->write(NAK);
        }
    } else if (strncmp(command, "write_output", 12) == 0) {
        if (attr_val >= 0 && attr_val <= 255) {
            sPort->write(ACK);
            events->notify_observers("output", attr_val);
        } else {
            sPort->write(NAK);
        }
    } else if (strncmp(command, "write_kp", 8) == 0) {
        if (attr_val >= 0 && attr_val <= 1000) {
            sPort->write(ACK);
            events->notify_observers("kp", attr_val);
        } else {
            sPort->write(NAK);
        }
    } else if (strncmp(command, "write_ki", 8) == 0) {
        if (attr_val >= 0 && attr_val <= 1000) {
            sPort->write(ACK);
            events->notify_observers("ki", attr_val);
        } else {
            sPort->write(NAK);
        }
    } else if (strncmp(command, "write_kd", 8) == 0) {
        if (attr_val >= 0 && attr_val <= 1000) {
            sPort->write(ACK);
            events->notify_observers("kd", attr_val);
        } else {
            sPort->write(NAK);
        }
    } else if (strncmp(command, "write_mode", 10) == 0) {
        if (attr_val >= 0 && attr_val <= 1) {
            sPort->write(ACK);
            events->notify_observers("mode", attr_val);
        } else {
            sPort->write(NAK);
        }
    } else if (strncmp(command, "save", 4) == 0) {
        sPort->write(ACK);
        events->notify_observers("write_memory", 1);
    } else if (strncmp(command, "reset", 5) == 0) {
        sPort->write(ACK);
        events->notify_observers("read_memory", 1);
    } else if (strncmp(command, "alerts", 5) == 0) {
        snprintf(message, 25, "Fan:%d Sensor:%d Temp:%d", alm_fail_fan, alm_fail_sensor, alm_high_temp);
        send_data(message);
    } else {
        sPort->write(NAK);
    }
}
