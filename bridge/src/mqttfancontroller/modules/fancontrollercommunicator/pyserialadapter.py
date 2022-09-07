import serial


class PyserialAdapter:
    """Adapter between Commands and Pyserial library"""

    _serial: serial.Serial

    def __init__(self, port: str, bauds: int):
        """Init a new adapter"""
        self._serial = serial.Serial(port, bauds, timeout=5)

    def read_uint8(self):
        rcvd_bytes = self._serial.read()
        if rcvd_bytes == b"":
            raise ResponseTimeoutError()

        rcvd_int = int.from_bytes(rcvd_bytes, "little")
        return rcvd_int

    # def _read_int8(self):
    #     received = self._read_uint8()
    #     return received - 128

    def read_uint16(self):
        rcvd_bytes = self._serial.read(2)
        if rcvd_bytes == b"":
            raise ResponseTimeoutError()

        rcvd_int = int.from_bytes(rcvd_bytes, "little")
        return rcvd_int

    def read_int16(self):
        received = self.read_uint16()
        return received - 32768

    def write_uint8(self, data: int):
        bytedata = data.to_bytes(1, "little")
        self._serial.write(bytedata)

    # def _write_int8(self, data: int):
    #     bytedata = (data + 128).to_bytes(1, "little")
    #     self._serial.write(bytedata)

    def write_uint16(self, data: int):
        bytedata = data.to_bytes(2, "little")
        self._serial.write(bytedata)

    # def _write_int16(self, data: int):
    #     bytedata = (data + 32768).to_bytes(2, "little")
    #     self._serial.write(bytedata)

    def reset_serial_buffer(self):
        """Reset the serial port buffer"""
        self._serial.reset_serial_buffer()
