"""
Python serial tester for Arduino controller.

Requirements:
- pyserial
- crc

Usage example:

For setting the temperature target to 20.00 C:

Input: WRITE_TARGET,2000<enter>
Expected response: ACK

The target should now be changed.
"""

import serial
import curses
import time
from crc import Calculator, Configuration

send_commands = {
    "NUL": b'\x00',
    "SOH": b'\x01',
    "STX": b'\x02',
    "ETX": b'\x03',
    "EOT": b'\x04',
    "ENQ": b'\x05',
    "ACK": b'\x06',
    "BEL": b'\x07',
    "NAK": b'\x08',
    "READ_TEMP": b'\x21', # !
    "READ_TARGET": b'\x22', # "
    "READ_SPEED": b'\x23', # #
    "READ_PWM": b'\x24', # $
    "READ_KP": b'\x25', # %
    "READ_KI": b'\x26', # &
    "READ_KD": b'\x27', # '
    "READ_MODE": b'\x28', # (
    "READ_ALARM": b'\x29', # )
    "WRITE_TEMP": b'\x31', # 1
    "WRITE_TARGET": b'\x32', # 2
    "WRITE_SPEED": b'\x33', # 3
    "WRITE_PWM": b'\x34', # 4
    "WRITE_KP": b'\x35', # 5
    "WRITE_KI": b'\x36', # 6
    "WRITE_KD": b'\x37', # 7
    "WRITE_MODE": b'\x38', # 8
    "WRITE_ALARM": b'\x39', # 9
}

text_buffer = list()
message_buffer = ""
input_line_position = 0
ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=5)

crc_conf = Configuration(
    width=16,
    polynomial=0x1021,
    init_value=0xFFFF,
    final_xor_value=0,
    reverse_input=False,
    reverse_output=False
)
crc_calculator = Calculator(crc_conf)


def get_byte_str(bytedata):
    return "".join("\\x{:02x}".format(letter) for letter in bytedata)


def read_byte():
    global text_buffer
    global ser
    global message_buffer
    rcvd_byte = ser.read()
    if rcvd_byte == send_commands["STX"]:
        if message_buffer:
            text_buffer.append(f"Unhandled data: {message_buffer}")
        message_buffer = ""
    elif rcvd_byte == send_commands["ETX"]:
        crc_sum = crc_calculator.checksum(message_buffer[:-4].encode("ascii"))
        crc_sum_str = format(crc_sum, "04X")
        crc_ok = crc_sum_str == message_buffer[-4:]
        text_buffer.append(f"Rx: {message_buffer}, CRC {'OK' if crc_ok else 'NOT OK'}, calculated from {message_buffer[:-4].encode('ascii')}")
        message_buffer = ""
    elif rcvd_byte == send_commands["ACK"]:
        text_buffer.append("Rx: ACK")
    elif rcvd_byte == send_commands["NAK"]:
        text_buffer.append("Rx: NAK")
    else:
        message_buffer += rcvd_byte.decode("ascii")
    return rcvd_byte


def tx_to_controller(parts: list):
    """Command sequence for writing data to the controller"""
    global text_buffer
    global ser
    payload = ""

    cmd = send_commands[parts[0]]
    if (len(parts) > 1):
        payload = parts[1]

    crc_sum = crc_calculator.checksum(
        f"{cmd.decode('ascii')}{payload}".encode('utf-8'))

    crc_sum_str = format(crc_sum, "04X")

    ser.write(send_commands["STX"])
    ser.write(cmd)
    ser.write(payload.encode("utf-8"))
    ser.write(crc_sum_str.encode("utf-8"))
    ser.write(send_commands["ETX"])

    text_buffer.append(
        f"Tx: {cmd.decode('ascii')}{payload} [CRC:{crc_sum_str}]")


def read_user_input(message: str) -> str:
    global input_line_position
    stdscr.move(2, 0)
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


def main(stdscr):
    global text_buffer
    global ser
    global input_line_position
    auto_report = False
    previous_autoreport = time.monotonic()
    max_y, _ = stdscr.getmaxyx()
    input_line_position = max_y - 3
    result = False
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)
    stdscr.clear()

    ser.reset_input_buffer()

    line = f"i: input terminal, a: autoreporting (now: {auto_report}), q: quit  "
    stdscr.addstr(0, 0, line)

    while True:
        c = stdscr.getch()
        if c == ord('q') or c == ord('Q'):
            break

        if c == ord('a') or c == ord('A'):
            auto_report = not auto_report
            line = f"i: input terminal, a: autoreporting (now: {auto_report}), q: quit  "
            stdscr.addstr(0, 0, line)

        if c == ord('i') or c == ord('I'):
            str_input = read_user_input("Command sequence: ")
            parts = str_input.split(",")
            if parts[0] in send_commands:
                tx_to_controller(parts)
            else:
                text_buffer.append(f"Bad sequence, not sending: {str_input}")

        if auto_report and (time.monotonic() - previous_autoreport > 10):
            previous_autoreport = time.monotonic()
            text_buffer.append("Requesting reports...")


        while ser.in_waiting > 0:
            result = read_byte()

        if text_buffer:
            max_y, _ = stdscr.getmaxyx()
            input_line_position = max_y - 3

        for i in range(len(text_buffer)):
            line = text_buffer.pop(0)

            stdscr.move(2, 0)
            stdscr.deleteln()
            stdscr.addstr(input_line_position, 0, line)
            stdscr.move(input_line_position + 1, 0)

        time.sleep(0.01)

    ser.close()


if __name__ == "__main__":
    e_msg = "OK"
    stdscr = curses.initscr()

    try:
        main(stdscr)
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
