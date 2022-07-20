"""
Python serial tester for Arduino controller.

Usage example:

For setting the temperature target on channel 1 to 20.00 C:

Input: 1,65,1,2000<enter>
Expected responses: ACK, RCVD, RCVD, RCVD (data is written in four parts)

The target should now be changed.
"""

import serial

response_names = {
    1: "HELLO",
    2: "ACK",
    3: "RCVD",
    6: "END",
    7: "ERROR",
    64: "TEMPERATURE",
    65: "TARGET",
    66: "FANSPD",
    67: "PIDOUT",
    68: "KP",
    69: "KI",
    70: "KD",
    71: "MODE",
}

def get_byte_str(bytedata):
    return "".join("\\x{:02x}".format(letter) for letter in bytedata)

def read_uint8():
    rcvd_bytes = ser.read()
    rcvd_int = int.from_bytes(rcvd_bytes, 'big')
    if rcvd_int > 0:
        print(f"Response: {response_names[rcvd_int]} ({get_byte_str(rcvd_bytes)})")
    else:
        print("No more data from Arduino.")
    return rcvd_int

def write_uint8(data: int):
    bytedata = data.to_bytes(1, "big")
    print("Writing: " + get_byte_str(bytedata))
    ser.write(bytedata)

def write_uint16(data: int):
    bytedata = data.to_bytes(2, "big")
    print("Writing: " + get_byte_str(bytedata))
    ser.write(bytedata)

data_write_method = {
    64: write_uint16,
    65: write_uint16,
    66: write_uint16,
    67: write_uint16,
    68: write_uint16,
    69: write_uint16,
    70: write_uint16,
    71: write_uint8,
}

ser = serial.Serial("/dev/ttyACM0", 9600, timeout=5)

print("Serial tester. Q quits.\n")

while True:
    str_input = input("Input: ")
    if str_input.upper() == "Q":
        break

    parts = str_input.split(",")

    if len(parts) == 4:
        if int(parts[1]) not in data_write_method:
            print("Unknown command")
            continue

        write_uint8(int(parts[0]))
        response = read_uint8()
        if response != 2:
            print("Got unexpected response on HELLO, aborting...")
            continue

        write_uint8(int(parts[1]))
        response = read_uint8()
        if response != 3:
            print("Got unexpected response on COMMAND, aborting...")
            continue

        write_uint8(int(parts[2]))
        response = read_uint8()
        if response != 3:
            print("Got unexpected response on channel select, aborting...")
            continue

        data_write_method[int(parts[1])](int(parts[3]))
        response = read_uint8()
        if response != 3:
            print("Got unexpected response, data apparently not received...")
            continue
    else:
        try:
            int_input = int(str_input)
            if int_input >= 0 and int_input <= 255:
                write_uint8(int_input)
            elif int_input >= 256 and int_input <= 65535:
                write_uint16(int_input)
            else:
                print("Input too low or big.")
        except ValueError:
            print("Reading only...")

    response = read_uint8()
    while response > 0:
        response = read_uint8()

print("Bye!")
ser.close()
