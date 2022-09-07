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
        self._tries = 0
        self._result = None
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

        self._serial_adapter.reset_serial_buffer()

        # Initiate connection
        self._serial_adapter.write_uint8(self._command_values["HELLO"])
        if self._serial_adapter.read_uint8() != self._command_values["ACK"]:
            raise UnexpectedResponseError("Unexpected return value on initialization")

        # Send command and channel
        self._serial_adapter.write_uint8(self._command_id)
        self._serial_adapter.write_uint8(self._channel)

        self._run_command_specific_tasks()

    def set_channel(self, channel: int):
        self._channel = channel

    @property
    def tries(self) -> int:
        """Get the number of tries already done"""
        return self._tries

    @property
    def result(self) -> dict:
        """Gets the result of the command"""
        return self._result

    def _run_command_specific_tasks(self):
        """Command-specific tasks. Override this in concrete implementations."""
        raise NotImplementedError()


class BaseSetCommand(AbstractCommand):
    """Base SET command"""
    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._value = None

    def execute(self) -> dict:
        """Executes the command"""
        super().execute()

        # Expect a response from the controller
        response = self._serial_adapter.read_uint8()
        if response != self._command_values["RCVD"]:
            raise UnexpectedResponseError("Unexpected response")

    def set_value(self, value):
        self._value = int(value)


class BaseGetCommand(AbstractCommand):
    """Base GET command"""
    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)

    def execute(self) -> dict:
        """Executes the command"""
        super().execute()

        # Always respond with RCVD since this bridge should only forward
        # the data to MQTT broker.
        self._serial_adapter.write_uint8(self._command_values["RCVD"])


class SetTargetCommand(BaseSetCommand):
    """Command to set target temperature of fan controller"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_id = self._command_values["SET_TARGET"]

    def set_value(self, value: int):
        self._value = int(value * 10)

    def _run_command_specific_tasks(self):
        """Sends value and expects RCVD response"""
        self._serial_adapter.write_uint16(self._value)


class SetOutputCommand(BaseSetCommand):
    """Command to set the output of fan controller"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_id = self._command_values["SET_OUTPUT"]

    def _run_command_specific_tasks(self):
        """Sends value and expects RCVD response"""
        self._serial_adapter.write_uint8(self._value)



class SetKPCommand(BaseSetCommand):
    """Command to set KP of fan controller"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_id = self._command_values["SET_KP"]

    def set_value(self, value: int):
        self._value = int(value * 100)

    def _run_command_specific_tasks(self):
        """Sends value and expects RCVD response"""
        self._serial_adapter.write_uint16(self._value)


class SetKICommand(BaseSetCommand):
    """Command to set KI of fan controller"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_id = self._command_values["SET_KI"]

    def set_value(self, value: int):
        self._value = int(value * 100)

    def _run_command_specific_tasks(self):
        """Sends value and expects RCVD response"""
        self._serial_adapter.write_uint16(self._value)


class SetKDCommand(BaseSetCommand):
    """Command to set KD of fan controller"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_id = self._command_values["SET_KD"]

    def set_value(self, value: int):
        self._value = int(value * 100)

    def _run_command_specific_tasks(self):
        """Sends value and expects RCVD response"""
        self._serial_adapter.write_uint16(self._value)



class SetModeCommand(BaseSetCommand):
    """Command to set the mode of fan controller"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_id = self._command_values["SET_MODE"]

    def _run_command_specific_tasks(self):
        """Sends value and expects RCVD response"""
        self._serial_adapter.write_uint8(self._value)


class GetStatusCommand(BaseGetCommand):
    """Get status of controller for specific channel and forward it to MQTT"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_id = self._command_values["GET_STATUS"]
        self._result = {
            "event": "controller_status",
            "data": {
                "channel": None,
                "temp": None,
                "target": None,
                "speed": None,
                "output": None,
            },
        }

    def _run_command_specific_tasks(self):
        """Gets four 2-byte values as _data"""
        self._result["data"]["channel"] = self._channel

        response = self._serial_adapter.read_int16()
        self._result["data"]["temp"] = response / 10

        response = self._serial_adapter.read_int16()
        self._result["data"]["target"] = response / 10

        response = self._serial_adapter.read_int16()
        self._result["data"]["speed"] = response

        response = self._serial_adapter.read_int16()
        self._result["data"]["output"] = response


class GetSettingsCommand(BaseGetCommand):
    """Get settings of controller for specific channel and forward it to MQTT"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_id = self._command_values["GET_SETTINGS"]
        self._result = {
            "event": "controller_settings",
            "data": {
                "channel": None,
                "mode": None,
                "kp": None,
                "ki": None,
                "kd": None,
            },
        }

    def _run_command_specific_tasks(self):
        """Gets four 2-byte values as _data"""
        self._result["data"]["channel"] = self._channel

        response = self._serial_adapter.read_uint16()
        self._result["data"]["mode"] = response

        response = self._serial_adapter.read_uint16()
        self._result["data"]["kp"] = response / 100

        response = self._serial_adapter.read_uint16()
        self._result["data"]["ki"] = response / 100

        response = self._serial_adapter.read_uint16()
        self._result["data"]["kd"] = response / 100

