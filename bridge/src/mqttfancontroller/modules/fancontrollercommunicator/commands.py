from abc import ABC

from mqttfancontroller.modules.fancontrollercommunicator.errors import (
    UnexpectedResponseError,
)
from mqttfancontroller.modules.fancontrollercommunicator.pyserialadapter import (
    PyserialAdapter,
)


class AbstractCommand(ABC):
    """Command to be delivered to the controller"""

    def __init__(self, serial_adapter: PyserialAdapter):
        """Init basic command.

        Inject serial library reference"""
        self._serial_adapter = serial_adapter

        self._serial_adapter: PyserialAdapter
        self._command_id = 0
        self._channel = 0
        self._value = None
        self._tries = 0
        self._command_values = {
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
        }

    def execute(self) -> dict:
        """Executes the command"""
        self._tries += 1
        self._initiate_connection()
        self._send_command_and_channel()
        self._run_command_specific_tasks()

    def set_channel(self, channel: int):
        self._channel = channel

    def set_value(self, value: int):
        self._value = value

    @property
    def tries(self) -> int:
        """Get the number of tries already done"""
        return self._tries

    def _run_command_specific_tasks(self):
        """Command-specific tasks. Override this in concrete implementations."""
        raise NotImplementedError()

    def _initiate_connection(self):
        """Initiate connection to fan controller"""
        self._serial_adapter.reset_serial_buffer()
        self._serial_adapter.write_uint8(self._command_values["HELLO"])
        if self._serial_adapter.read_uint8() != self._command_values["ACK"]:
            raise UnexpectedResponseError("Unexpected return value on initialization")

    def _send_command_and_channel(self):
        """Sends command and channel bytes. These are always in the same
        order so it's ok to combine them here."""
        self._serial_adapter.write_uint8(self._command_id)
        self._serial_adapter.write_uint8(self._channel)


class SetTargetCommand(AbstractCommand):
    """Command to set target temperature of fan controller"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_id = self._command_values["SET_TARGET"]

    def set_value(self, value: int):
        self._value = value * 10

    def _run_command_specific_tasks(self):
        """Sends value and expects RCVD response"""
        self._serial_adapter.write_uint16(self._value)
        response = self._serial_adapter.read_uint8()
        if response != self._command_values["RCVD"]:
            raise UnexpectedResponseError("Unexpected response")
