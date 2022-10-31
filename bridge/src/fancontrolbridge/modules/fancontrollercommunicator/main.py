# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import json
import logging

from fancontrolbridge.modules.fancontrollercommunicator.commands import (
    SetTargetCommand,
    SetOutputCommand,
    SetKPCommand,
    SetKICommand,
    SetKDCommand,
    SetModeCommand,
    GetStatusCommand,
    GetSettingsCommand,
)
from fancontrolbridge.modules.fancontrollercommunicator.errors import (
    ErrorResponseError,
    ResponseTimeoutError,
    UnexpectedResponseError,
    WriteTimeoutError,
)
from fancontrolbridge.modules.fancontrollercommunicator.pyserialadapter import (
    PyserialAdapter,
)
from fancontrolbridge.utils.baseprocess import BaseProcessABC
from fancontrolbridge.utils.component import BaseComponentABC


class main(BaseProcessABC, BaseComponentABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(
            "fancontrolbridge.modules.serialcommunicator")
        self._send_queue = list()
        self._serial_adapter = PyserialAdapter(
            self.config["port"], self.config["bauds"]
        )
        self.events.register_observer(self.config["command_topic"], self)
        self._commands = {
            "SET_TARGET": SetTargetCommand,
            "SET_OUTPUT": SetOutputCommand,
            "SET_KP": SetKPCommand,
            "SET_KI": SetKICommand,
            "SET_KD": SetKDCommand,
            "SET_MODE": SetModeCommand,
            "GET_STATUS": GetStatusCommand,
            "GET_SETTINGS": GetSettingsCommand,
        }

    def update(self):
        """Handle the oldest command object, if any in queue"""
        if not self._send_queue:
            return

        message = "OK"
        success = False
        remove_command = False

        command_object = self._send_queue[0]

        try:
            self.logger.debug(f"Executing: {command_object}")
            command_object.execute()
            self.logger.debug(f"Execution finished for {command_object}")
            if command_object.result_event is not None:
                self.publish_global_event(command_object.result_event, command_object.result_data)
        except (OverflowError, TypeError, AttributeError) as e:
            remove_command = True
            message = str(e)
        except (UnexpectedResponseError, ErrorResponseError, ResponseTimeoutError, WriteTimeoutError) as e:
            message = str(e)
        else:
            success = True
            remove_command = True

        if command_object.tries >= 3:
            self.logger.warning(
                f"Command execution failed too many times: {command_object}")
            remove_command = True

        if remove_command:
            self._send_queue.pop(0)
            self.publish_global_event(
                "controller_command_results",
                {
                    "type": "success" if success else "error",
                    "message": message,
                    "original_command": str(command_object),
                },
            )

    def notify(self, event, data):
        """Generates command objects from event data.

        Expects data to be a dict containing "command" and "channel".
        Might also contain "value" (mandatory for SET_* commands, not used
        in GET_* commands)
        """
        command_object = None
        try:
            data_dict = json.loads(data)
            if "command" not in data or "channel" not in data_dict:
                self.logger.debug("Command or channel not found in data")
                return

            if data_dict["command"] in self._commands.keys():
                command_object = self._commands[data_dict["command"]](
                    self._serial_adapter
                )
                command_object.set_channel(data_dict["channel"])

                if "value" in data_dict and data_dict["command"] in [
                    "SET_TARGET",
                    "SET_OUTPUT",
                    "SET_KP",
                    "SET_KI",
                    "SET_KD",
                    "SET_MODE",
                ]:
                    command_object.set_value(data_dict["value"])

                self.logger.debug("Message seems ok. Appending to queue.")
                self._send_queue.append(command_object)
        except ValueError:
            self.logger.debug(
                f"Data is not a dictionary. ValueError in main.notify.")
        except (OverflowError, AttributeError, TypeError) as e:
            self.logger.debug(f"Error in main.notify: {e}")
            self.publish_global_event(
                "controller_command_results",
                {
                    "type": "error",
                    "message": str(e),
                    "original_command": f"{data_dict['command']} / {data_dict['channel']}",
                },
            )
