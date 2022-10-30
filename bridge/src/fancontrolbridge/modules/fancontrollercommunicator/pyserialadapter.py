import serial
from fancontrolbridge.modules.fancontrollercommunicator.errors import (
    ResponseTimeoutError, WriteTimeoutError
)


class PyserialAdapter:
    """Adapter between Commands and Pyserial library"""

    _serial: serial.Serial

    def __init__(self, port: str, bauds: int):
        self._serial = serial.Serial(port, bauds, timeout=5, write_timeout=5)

    def read_uint8(self):
        rcvd_bytes = self._serial.read()
        if rcvd_bytes == b"":
            raise ResponseTimeoutError("Response timeout")

        rcvd_int = int.from_bytes(rcvd_bytes, "little")
        return rcvd_int

    def read_uint16(self):
        rcvd_bytes = self._serial.read(2)
        if rcvd_bytes == b"":
            raise ResponseTimeoutError("Response timeout")

        rcvd_int = int.from_bytes(rcvd_bytes, "little")
        return rcvd_int

    def read_int16(self):
        received = self.read_uint16()
        return received - 32768

    def write_uint8(self, data: int):
        bytedata = data.to_bytes(1, "little")
        try:
            self._serial.write(bytedata)
        except serial.SerialTimeoutException as e:
            raise WriteTimeoutError("Write timeout")

    def write_uint16(self, data: int):
        bytedata = data.to_bytes(2, "little")
        try:
            self._serial.write(bytedata)
        except serial.SerialTimeoutException as e:
            raise WriteTimeoutError("Write timeout")

    def reset_both_buffers(self):
        self._serial.reset_input_buffer()
        self._serial.reset_output_buffer()
