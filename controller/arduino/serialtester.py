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

commands = {
    "HELLO": 1,
    "ACK": 2,
    "RCVD": 3,
    "END": 6,
    "ERROR": 7,
    "SET_TARGET": 64,
    "SET_OUTPUT": 65,
    "SET_KP": 66,
    "SET_KI": 67,
    "SET_KD": 68,
    "SET_MODE": 69,
    "GET_STATUS": 70,
    "GET_SETTINGS": 71,
    "REPORT_STATUS": 72,
    "REPORT_SETTINGS": 73,
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
        text_buffer.append(f"Rx: {get_byte_str(rcvd_bytes)}")
    else:
        text_buffer.append("No data received.")
    return rcvd_int

def read_uint16():
    global text_buffer
    global ser
    rcvd_bytes = ser.read(2)
    rcvd_int = int.from_bytes(rcvd_bytes, "little")
    if rcvd_int > 0:
        text_buffer.append(f"Rx: {get_byte_str(rcvd_bytes)}")
    else:
        text_buffer.append("No data received.")
    return rcvd_int

def read_int16():
    received = read_uint16()
    return received - 32768

def write_uint8(data: int):
    global text_buffer
    global ser
    bytedata = data.to_bytes(1, "little")
    text_buffer.append("Tx: " + get_byte_str(bytedata))
    ser.write(bytedata)


def write_uint16(data: int):
    global text_buffer
    global ser
    bytedata = data.to_bytes(2, "little")
    text_buffer.append("Tx: " + get_byte_str(bytedata))
    ser.write(bytedata)

def read_status():
    received = read_int16()
    text_buffer.append(f"Interpreted as {received/10}")
    received = read_int16()
    text_buffer.append(f"Interpreted as {received/10}")
    received = read_int16()
    text_buffer.append(f"Interpreted as {received}")
    received = read_int16()
    text_buffer.append(f"Interpreted as {received}")

    write_uint8(commands["RCVD"])
    return True

def read_settings():
    received = read_uint16()
    text_buffer.append(f"Interpreted as {received}")
    received = read_uint16()
    text_buffer.append(f"Interpreted as {received/100}")
    received = read_uint16()
    text_buffer.append(f"Interpreted as {received/100}")
    received = read_uint16()
    text_buffer.append(f"Interpreted as {received/100}")

    write_uint8(commands["RCVD"])
    return True

def write_sequence(parts: list) -> bool:
    """Command sequence for writing data to the controller"""
    global text_buffer
    if int(parts[0]) not in data_write_method:
        text_buffer.append("Unknown command")
        return False

    write_uint8(commands["HELLO"])
    response = read_uint8()
    if response != commands["ACK"]:
        text_buffer.append("Got unexpected response on HELLO, aborting...")
        return False

    write_uint8(int(parts[0]))
    write_uint8(int(parts[1]))

    # Writing data is always a simple task of writing n number of bytes
    # Response should be byte \x03, so we may just read it here
    data_write_method[int(parts[0])](int(parts[2]))
    response = read_uint8()
    if response == commands["RCVD"]:
        return True
    else:
        text_buffer.append(f"Unexpected response (was: {response}).")

    text_buffer.append("Transfer failed.")
    return False

def read_sequence(parts: list) -> bool:
    global text_buffer
    if int(parts[0]) not in data_read_method:
        text_buffer.append("Unknown command")
        return False

    write_uint8(commands["HELLO"])
    response = read_uint8()
    if response != commands["ACK"]:
        text_buffer.append("Got unexpected response on HELLO, aborting...")
        return False

    write_uint8(int(parts[0]))
    write_uint8(int(parts[1]))

    # Receiving data is more complicated than sending commands, so we'll
    # expect boolean from the method instead of reading single byte here.
    return data_read_method[int(parts[0])]()

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
    70: read_status,
    71: read_settings,
}

def main(stdscr):
    global text_buffer
    global ser
    global input_line_position
    max_y, _ = stdscr.getmaxyx()
    input_line_position = max_y - 2
    result = False
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
            str_input = read_user_input("Command sequence: ")
            parts = str_input.split(",")
            if len(parts) == 2:
                text_buffer.append(f"Sending READ sequence: {str_input}")
                result = read_sequence(parts)
            elif len(parts) == 3:
                text_buffer.append(f"Sending WRITE sequence: {str_input}")
                result = write_sequence(parts)
            else:
                text_buffer.append(f"Bad sequence, not sending: {str_input}")

            if not result:
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
