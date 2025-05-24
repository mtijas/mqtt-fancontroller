#include "serialcomms.hpp"

SerialComms::SerialComms(IObservable *events, int update_interval,
                         const byte rxPin, const byte txPin)
    : TimedComponent(events, update_interval) {
    this->sPort = new SoftwareSerial(rxPin, txPin);
    this->bauds = 9600;
}

void SerialComms::setup(int bauds) {
    this->bauds = bauds;
    sPort->begin(bauds);
    sPort->listen();
    send_data("MQTT Fan Controller");
    sPort->write(LF);
    show_help();
    sPort->write(LF);
    events->register_observer(this);
}

void SerialComms::setup() { setup(9600); }

void SerialComms::notify(const char *event, int payload) {
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
    if (!sPort->available()) {
        return;
    }

    char received = sPort->read();
    if (received == CR) {
        sPort->write(CR);
        sPort->write(LF);

        handle_message();

        message_buffer[0] = '\n';
        message_length = 0;
    } else if (received == BS || received == DEL) {
        if (message_length > 0) {
            message_length--;
            message_buffer[message_length] = '\n';
            sPort->write(BS);
            sPort->write(' ');
            sPort->write(BS);
        }
    } else if (received >= ASCII_PRINTABLE_LOWER_LIMIT &&
               received <= ASCII_PRINTABLE_UPPER_LIMIT) {
        // Received byte was printable. Limit message length to 63 chars to
        // accommodate EOL char.
        if (message_length < 63) {
            sPort->write(received);
            message_buffer[message_length] = received;
            message_length++;
            message_buffer[message_length] = '\n';
        } else {
            // Input message buffer full. Indicate that by NAKing
            // every received char until known control char is
            // received. Not a good solution but at least we don't
            // ghost the sender completely.
            send_data("Input buffer full!");
            sPort->write(NAK);
        }
    } else {
        sPort->write(NAK);
    }
}

void SerialComms::send_data(const char *data) {
    char *ptr = data;

    for (char c = *ptr; c; c = *++ptr) {
        if (c == '\n') {
            break;
        }
        sPort->write(c);
    }

    sPort->write(CR);
    sPort->write(LF);
}

void SerialComms::handle_message() {
    if (message_buffer[0] == '\n') {
        return;
    }

    char message[32];
    int attr_val = -999;

    // Payload is anything but CRC, assume 32 chars max.
    char command[32];
    char attribute[32];
    command[0] = '\n';
    attribute[0] = '\n';
    int position = 0;
    int part = 0;
    for (int i = 0; i < message_length; i++) {
        char chr = message_buffer[i];
        if (chr == ' ') {
            part++;
            position = 0;
        } else {
            if (part == 0) {
                command[position] = chr;
                command[position + 1] = '\n';
            } else {
                attribute[position] = chr;
                attribute[position + 1] = '\n';
            }
            position++;
        }
    }

    if (attribute[0] != '\n') {
        attr_val = atoi(attribute);
    }

    if (strncmp(command, "temp", 4) == 0) {
        snprintf(message, 12, "%d", temp);
        send_data(message);
    } else if (strncmp(command, "target", 6) == 0) {
        if (part == 0) {
            snprintf(message, 12, "%d", target);
            send_data(message);
        } else {
            if (attr_val >= 0 && attr_val <= 1500) {
                send_data("OK");
                events->notify_observers("target", attr_val);
            } else {
                send_data("Error. Limit to 0-1500.");
            }
        }
    } else if (strncmp(command, "speed", 5) == 0) {
        snprintf(message, 12, "%d", speed);
        send_data(message);
    } else if (strncmp(command, "pwm", 3) == 0) {
        if (part == 0) {
            snprintf(message, 4, "%d", output);
            send_data(message);
        } else {
            if (attr_val >= 0 && attr_val <= 255) {
                send_data("OK");
                events->notify_observers("output", attr_val);
            } else {
                send_data("Error. Limit to 0-255.");
            }
        }
    } else if (strncmp(command, "KP", 2) == 0) {
        if (part == 0) {
            snprintf(message, 12, "%d", kp);
            send_data(message);
        } else {
            if (attr_val >= 0 && attr_val <= 1000) {
                send_data("OK");
                events->notify_observers("kp", attr_val);
            } else {
                send_data("Error. Limit to 0-1000.");
            }
        }
    } else if (strncmp(command, "KI", 2) == 0) {
        if (part == 0) {
            snprintf(message, 12, "%d", ki);
            send_data(message);
        } else {
            if (attr_val >= 0 && attr_val <= 1000) {
                send_data("OK");
                events->notify_observers("ki", attr_val);
            } else {
                send_data("Error. Limit to 0-1000.");
            }
        }
    } else if (strncmp(command, "KD", 2) == 0) {
        if (part == 0) {
            snprintf(message, 12, "%d", kd);
            send_data(message);
        } else {
            if (attr_val >= 0 && attr_val <= 1000) {
                send_data("OK");
                events->notify_observers("kd", attr_val);
            } else {
                send_data("Error. Limit to 0-1000.");
            }
        }
    } else if (strncmp(command, "mode", 4) == 0) {
        if (part == 0) {
            snprintf(message, 2, "%d", mode);
            send_data(message);
        } else {
            if (attr_val >= 0 && attr_val <= 1) {
                send_data("OK");
                events->notify_observers("mode", attr_val);
            } else {
                send_data("Error. [0: MANUAL; 1: AUTO].");
            }
        }
    } else if (strncmp(command, "save", 4) == 0) {
        send_data("OK");
        events->notify_observers("write_memory", 1);
    } else if (strncmp(command, "load", 4) == 0) {
        send_data("OK");
        events->notify_observers("read_memory", 1);
    } else if (strncmp(command, "alerts", 5) == 0) {
        snprintf(message, 25, "Fan:%d Sensor:%d Temp:%d", alm_fail_fan,
                 alm_fail_sensor, alm_high_temp);
        send_data(message);
    } else if (strncmp(command, "help", 4) == 0) {
        show_help();
    } else {
        send_data("Unknown command!");
    }
}

void SerialComms::show_help() {
    send_data("Commands:");
    send_data("temp");
    send_data("speed");
    send_data("target [<0-1500>]");
    send_data("pwm [<0-255>]");
    send_data("KP [<0-1000>]");
    send_data("KI [<0-1000>]");
    send_data("KD [<0-1000>]");
    send_data("mode [0|1]");
    send_data("save");
    send_data("load");
    send_data("alerts");
    send_data("help");
}
