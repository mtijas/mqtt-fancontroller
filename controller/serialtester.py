"""
Python serial tester for Arduino controller.

Requirements:
- pyserial
- crc

Usage example:

For setting the temperature target to 20.0 C:

Input: write_target 200<enter>
Expected response: ACK

The target should now be changed.
"""

import serial
import curses
import time

send_commands = {
    "NUL": b'\x00',
    "SOH": b'\x01',
    "STX": b'\x02',
    "ETX": b'\x03',
    "EOT": b'\x04',
    "ENQ": b'\x05',
    "ACK": b'\x06',
    "BEL": b'\x07',
    "LF": b'\x0A',
    "CR": b'\x0D',
    "NAK": b'\x15',
}

text_buffer = list()
message_buffer = ""
ser = serial.Serial("/dev/cu.usbserial-01348EC6", 9600, timeout=5)
cursor_position = 0


def get_byte_str(bytedata):
    return "".join("\\x{:02x}".format(letter) for letter in bytedata)


def read_byte():
    global text_buffer
    global ser
    global message_buffer
    global cursor_position
    max_y, _ = stdscr.getmaxyx()
    input_line_position = max_y - 1
    rcvd_byte = ser.read()
    if rcvd_byte == send_commands["LF"] or rcvd_byte == send_commands["CR"]:
        text_buffer.append((f"{message_buffer}", 1))
        message_buffer = ""
        cursor_position = 0
    elif rcvd_byte == send_commands["ACK"]:
        text_buffer.append(("ACK", 2))
    elif rcvd_byte == send_commands["NAK"]:
        text_buffer.append(("NAK", 3))
    else:
        try:
            message_buffer += rcvd_byte.decode("ascii")
            stdscr.addch(input_line_position, cursor_position, rcvd_byte.decode("ascii"))
            cursor_position += 1
        except UnicodeDecodeError as e:
            message_buffer += rcvd_byte.hex()

    return rcvd_byte


def main(stdscr):
    global text_buffer
    global ser
    global cursor_position
    max_y, _ = stdscr.getmaxyx()
    input_line_position = max_y - 1
    result = False
    str_input = ""
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)
    stdscr.clear()

    ser.reset_input_buffer()

    line = f"^C: quit. Enter sends."
    stdscr.addstr(0, 0, line)
    stdscr.move(input_line_position, 0)

    while True:
        c = stdscr.getch()

        # if c == curses.KEY_BACKSPACE or c == ord('\b') or c == 127:
        #     str_input = str_input[:-1]
        #     stdscr.delch(input_line_position, len(str_input))
        if c != curses.ERR:
            ser.write(chr(c).encode('utf-8'))

        while ser.in_waiting > 0:
            result = read_byte()

        for i in range(len(text_buffer)):
            line, color = text_buffer.pop(0)

            stdscr.move(2, 0)
            stdscr.deleteln()
            stdscr.addstr(input_line_position-1, 0, line, curses.color_pair(color))
            stdscr.move(input_line_position, 0)

        time.sleep(0.01)

    ser.close()


if __name__ == "__main__":
    e_msg = "OK"
    stdscr = curses.initscr()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

    try:
        main(stdscr)
    except KeyboardInterrupt as e:
        pass
    except Exception as e:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        e_msg = f"{e}"
        exit(-1)
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        print(f"Shutdown: {e_msg}")
