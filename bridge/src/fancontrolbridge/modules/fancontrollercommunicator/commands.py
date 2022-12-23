from abc import ABC

from fancontrolbridge.modules.fancontrollercommunicator.errors import (
    UnexpectedResponseError,
)
from fancontrolbridge.modules.fancontrollercommunicator.pyserialadapter import (
    PyserialAdapter,
)


class AbstractCommand(ABC):
    """Command to be delivered to the controller"""

    def __init__(self, serial_adapter: PyserialAdapter):
        """Init basic command.

        Inject serial library reference"""
        self._serial_adapter = serial_adapter

        self._serial_adapter: PyserialAdapter
        self._command_name = None
        self._channel = 0
        self._tries = 0
        self._event_suffix = None
        self._result_data = {}
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

        self._serial_adapter.reset_both_buffers()

        # Initiate connection
        self._serial_adapter.write_uint8(self._command_values["HELLO"])
        if self._serial_adapter.read_uint8() != self._command_values["ACK"]:
            raise UnexpectedResponseError("Unexpected return value on initialization")

        # Send command and channel
        self._serial_adapter.write_uint8(self._command_values[self._command_name])
        self._serial_adapter.write_uint8(self._channel)

        self._run_command_specific_tasks()

    def set_channel(self, channel: int):
        if type(channel) is not int:
            raise TypeError("Channel should be an integer")
        if channel < 1 or channel > 2:
            raise OverflowError("Channel should be 1 or 2")
        self._channel = channel

    @property
    def tries(self) -> int:
        """Get the number of tries already done"""
        return self._tries

    @property
    def result_data(self) -> dict:
        """Gets the result data of the command"""
        return self._result_data

    @property
    def result_event(self) -> dict:
        """Gets the result event of the command"""
        if self._event_suffix is None:
            return None
        return f"channel_{self._channel}_{self._event_suffix}"

    def __str__(self) -> str:
        return f"{self._command_name} / {self._channel}"

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
        if type(value) is not int:
            raise TypeError("Value should be an integer")
        self._value = int(value)

    def __str__(self) -> str:
        return f"{self._command_name} / {self._channel} / {self._value}"


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

    def __str__(self) -> str:
        return f"{self._command_name} / {self._channel}"


class SetTargetCommand(BaseSetCommand):
    """Command to set target temperature of fan controller"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_name = "SET_TARGET"

    def set_value(self, value: int):
        if type(value) is not int and type(value) is not float:
            raise TypeError(
                f"Value should be an integer or a float. Got {type(value)} instead."
            )
        if value < 0 or value > 6553.5:
            raise OverflowError("Target temp should be between 0 and 6553.5")

        self._value = int(round(value, 1) * 10)

    def _run_command_specific_tasks(self):
        """Sends value and expects RCVD response"""
        self._serial_adapter.write_uint16(self._value)


class SetOutputCommand(BaseSetCommand):
    """Command to set the output of fan controller"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_name = "SET_OUTPUT"

    def set_value(self, value: int):
        if type(value) is not int:
            raise TypeError(
                f"Value should be an integer. Got {type(value)} instead."
            )
        if value < 0 or value > 255:
            raise OverflowError("Output speed should be between 0 and 255")

        self._value = value

    def _run_command_specific_tasks(self):
        """Sends value and expects RCVD response"""
        self._serial_adapter.write_uint8(self._value)


class SetKPCommand(BaseSetCommand):
    """Command to set KP of fan controller"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_name = "SET_KP"

    def set_value(self, value: int):
        if type(value) is not int and type(value) is not float:
            raise TypeError("Value should be an integer or a float")
        self._value = round(value * 100)

    def _run_command_specific_tasks(self):
        """Sends value and expects RCVD response"""
        self._serial_adapter.write_uint16(self._value)


class SetKICommand(BaseSetCommand):
    """Command to set KI of fan controller"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_name = "SET_KI"

    def set_value(self, value: int):
        if type(value) is not int and type(value) is not float:
            raise TypeError("Value should be an integer or a float")
        self._value = round(value * 100)

    def _run_command_specific_tasks(self):
        """Sends value and expects RCVD response"""
        self._serial_adapter.write_uint16(self._value)


class SetKDCommand(BaseSetCommand):
    """Command to set KD of fan controller"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_name = "SET_KD"

    def set_value(self, value: int):
        if type(value) is not int and type(value) is not float:
            raise TypeError("Value should be an integer or a float")
        self._value = round(value * 100)

    def _run_command_specific_tasks(self):
        """Sends value and expects RCVD response"""
        self._serial_adapter.write_uint16(self._value)


class SetModeCommand(BaseSetCommand):
    """Command to set the mode of fan controller"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_name = "SET_MODE"

    def _run_command_specific_tasks(self):
        """Sends value and expects RCVD response"""
        self._serial_adapter.write_uint8(self._value)


class GetStatusCommand(BaseGetCommand):
    """Get status of controller for specific channel and forward it to MQTT"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_name = "GET_STATUS"
        self._event_suffix = "status"

    def _run_command_specific_tasks(self):
        """Gets four 2-byte values as _data"""
        response = self._serial_adapter.read_int16()
        self._result_data["temp"] = response / 10

        response = self._serial_adapter.read_int16()
        self._result_data["target"] = response / 10

        response = self._serial_adapter.read_int16()
        self._result_data["speed"] = response

        response = self._serial_adapter.read_int16()
        self._result_data["output"] = response


class GetSettingsCommand(BaseGetCommand):
    """Get settings of controller for specific channel and forward it to MQTT"""

    def __init__(self, serial_adapter: PyserialAdapter):
        super().__init__(serial_adapter)
        self._command_name = "GET_SETTINGS"
        self._event_suffix = "settings"

    def _run_command_specific_tasks(self):
        """Gets four 2-byte values as _data"""
        response = self._serial_adapter.read_uint16()
        self._result_data["mode"] = response

        response = self._serial_adapter.read_uint16()
        self._result_data["kp"] = response / 100

        response = self._serial_adapter.read_uint16()
        self._result_data["ki"] = response / 100

        response = self._serial_adapter.read_uint16()
        self._result_data["kd"] = response / 100
