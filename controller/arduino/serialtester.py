"""
Python serial tester for Arduino controller.

Usage example:

For setting the temperature target on channel 1 to 20.00 C:

Input: 1,64,1,2000<enter>
Expected responses: ACK, RCVD, RCVD, RCVD (data is written in four parts)

The target should now be changed.
"""

import serial
import curses
import time

response_names = {
    1: "HELLO",
    2: "ACK",
    3: "RCVD",
    6: "END",
    7: "ERROR",
    64: "SET_TARGET",
    65: "SET_OUTPUT",
    66: "SET_KP",
    67: "SET_KI",
    68: "SET_KD",
    69: "SET_MODE",
    70: "GET_DATA",
    71: "GET_SETTINGS",
}

text_buffer = list()
input_line_position = 0
ser = serial.Serial("/dev/ttyACM0", 9600, timeout=5)

def get_byte_str(bytedata):
    return "".join("\\x{:02x}".format(letter) for letter in bytedata)


def read_uint8():
    global text_buffer
    global ser
    rcvd_bytes = ser.read()
    rcvd_int = int.from_bytes(rcvd_bytes, "little")
    if rcvd_int > 0:
        text_buffer.append(f"Response: {response_names[rcvd_int]} ({get_byte_str(rcvd_bytes)})")
    else:
        text_buffer.append("No more data from Arduino.")
    return rcvd_int

def read_string():
    global text_buffer
    global ser
    rcvd = ser.readline()
    text_buffer.append(f"Response: {rcvd}")
    return rcvd

def write_uint8(data: int):
    global text_buffer
    global ser
    bytedata = data.to_bytes(1, "little")
    text_buffer.append("Writing: " + get_byte_str(bytedata))
    ser.write(bytedata)


def write_uint16(data: int):
    global text_buffer
    global ser
    bytedata = data.to_bytes(2, "little")
    text_buffer.append("Writing: " + get_byte_str(bytedata))
    ser.write(bytedata)

def write_sequence(parts: list) -> bool:
    """Command sequence for writing data to the controller"""
    global text_buffer
    if int(parts[0]) not in data_write_method:
        text_buffer.append("Unknown command")
        return False

    write_uint8(1)
    response = read_uint8()
    if response != 2:
        text_buffer.append("Got unexpected response on HELLO, aborting...")
        return False

    write_uint8(int(parts[0]))
    response = read_uint8()
    if response != 3:
        text_buffer.append("Got unexpected response on COMMAND, aborting...")
        return False

    write_uint8(int(parts[1]))
    response = read_uint8()
    if response != 3:
        text_buffer.append("Got unexpected response on channel select, aborting...")
        return False

    if int(parts[0]) in data_write_method:
        data_write_method[int(parts[0])](int(parts[2]))
        response = read_uint8()
        if response != 3:
            text_buffer.append("Got unexpected response, data apparently not received...")
            return False

    return True

def read_sequence(parts: list) -> bool:
    global text_buffer
    if int(parts[0]) not in data_read_method:
        text_buffer.append("Unknown command")
        return False

    write_uint8(1)
    response = read_uint8()
    if response != 2:
        text_buffer.append("Got unexpected response on HELLO, aborting...")
        return False

    write_uint8(int(parts[0]))
    response = read_uint8()
    if response != 3:
        text_buffer.append("Got unexpected response on COMMAND, aborting...")
        return False

    write_uint8(int(parts[1]))
    response = read_uint8()
    if response != 3:
        text_buffer.append("Got unexpected response on channel select, aborting...")
        return False

    if int(parts[0]) in data_read_method:
        data_read_method[int(parts[0])]()

    return True

def read_user_input(message: str) -> str:
    global input_line_position
    stdscr.move(0, 0)
    stdscr.deleteln()
    curses.echo()
    curses.nocbreak()
    stdscr.nodelay(False)
    stdscr.addstr(input_line_position, 0, message)
    stdscr.refresh()
    str_input = stdscr.getstr(input_line_position, len(message)).decode()
    curses.noecho()
    curses.cbreak()
    stdscr.nodelay(True)
    return str_input

data_write_method = {
    64: write_uint16,
    65: write_uint8,
    66: write_uint16,
    67: write_uint16,
    68: write_uint16,
    69: write_uint8,
}

data_read_method = {
    70: read_string,
    71: read_string,
}

def main(stdscr):
    global text_buffer
    global ser
    global input_line_position
    max_y, _ = stdscr.getmaxyx()
    input_line_position = max_y - 2
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)
    stdscr.clear()

    ser.reset_input_buffer()

    print("Serial tester. I opens input prompt, Q quits.\n")

    while True:
        c = stdscr.getch()
        if c == ord('q') or c == ord('Q'):
            break

        if c == ord('i') or c == ord('I'):
            tries = 0
            str_input = read_user_input("Command sequence: ")
            parts = str_input.split(",")
            if len(parts) == 2:
                text_buffer.append(f"Sending READ sequence: {str_input}")
                while tries < 3:
                    if read_sequence(parts):
                        break
                    tries += 1
            elif len(parts) == 3:
                text_buffer.append(f"Sending WRITE sequence: {str_input}")
                while tries < 3:
                    if write_sequence(parts):
                        break
                    tries += 1
            else:
                text_buffer.append(f"Bad sequence, not sending: {str_input}")

            if tries >= 3:
                text_buffer.append("Sending sequence failed. Is controller connected?")

        while ser.in_waiting > 0:
            read_uint8()

        if text_buffer:
            max_y, _ = stdscr.getmaxyx()
            input_line_position = max_y - 2

        for i in range(len(text_buffer)):
            line = text_buffer.pop(0)

            stdscr.move(0, 0)
            stdscr.deleteln()
            stdscr.addstr(input_line_position, 0, line)

        time.sleep(0.01)

    ser.close()

if __name__ == "__main__":
    stdscr = curses.initscr()

    try:
        main(stdscr)
    except Exception as e:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        print(f"Unexpected exception: {e}")
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
