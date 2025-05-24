#include "hd44780.hpp"

HD44780::HD44780(IObservable *events, int update_interval, int rs, int en,
                 int d4, int d5, int d6, int d7)
    : TimedComponent(events, update_interval) {
    this->rs = rs;
    this->en = en;
    this->d4 = d4;
    this->d5 = d5;
    this->d6 = d6;
    this->d7 = d7;
}

void HD44780::setup() {
    lcd = new LiquidCrystal(rs, en, d4, d5, d6, d7);
    lcd->begin(16, 2);
    lcd->clear();
    print_fmt(0, 0, "", "                ");
    print_fmt(0, 1, "    @", "                ");
    events->register_observer(this);
}

void HD44780::notify(const char *event, int payload) {
    if (strncmp(event, "temp", 4) == 0) {
        print_fmt(0, 0, payload, "     ");
    } else if (strncmp(event, "target", 6) == 0) {
        print_fmt(5, 0, payload, "     ");
    } else if (strncmp(event, "speed", 5) == 0) {
        print_fmt(0, 1, payload, "    ");
    } else if (strncmp(event, "output", 6) == 0) {
        print_fmt(5, 1, payload, "   ");
    } else if (strncmp(event, "mode", 4) == 0) {
        switch (payload) {
        case 0:
            print_fmt(10, 1, "MANUAL", "      ");
            break;
        case 1:
            print_fmt(10, 1, "  AUTO", "      ");
            break;
        default:
            print_fmt(10, 1, "ERROR!", "      ");
            break;
        }
    } else if (strncmp(event, "alm_fail_fan", 12) == 0) {
        print_fmt(14, 0, payload == 1 ? "F" : "f", " ");
    } else if (strncmp(event, "alm_high_temp", 13) == 0) {
        print_fmt(15, 0, payload == 1 ? "T" : "t", " ");
    } else if (strncmp(event, "alm_fail_sensor", 15) == 0) {
        print_fmt(13, 0, payload == 1 ? "S" : "s", " ");
    } else if (strncmp(event, "pending_write", 13) == 0) {
        print_fmt(12, 0, "W", " ");
    } else if (strncmp(event, "read_memory", 11) == 0) {
        print_fmt(12, 0, "w", " ");
    } else if (strncmp(event, "write_memory", 12) == 0) {
        print_fmt(12, 0, "w", " ");
    } else if (strncmp(event, "bootup_complete", 15) == 0) {
        print_fmt(12, 0, "w", " ");
    }
}

void HD44780::update() { return; }

void HD44780::print_fmt(int column, int row, const char *message,
                        const char *placeholder) {
    prepare_print_position(column, row, placeholder);
    lcd->print(message);
}

void HD44780::print_fmt(int column, int row, float message,
                        const char *placeholder) {
    prepare_print_position(column, row, placeholder);
    lcd->print(message);
}

void HD44780::print_fmt(int column, int row, int message,
                        const char *placeholder) {
    prepare_print_position(column, row, placeholder);
    lcd->print(message);
}

void HD44780::prepare_print_position(int column, int row,
                                     const char *placeholder) {
    lcd->setCursor(column, row);
    lcd->print(placeholder);
    lcd->setCursor(column, row);
}
