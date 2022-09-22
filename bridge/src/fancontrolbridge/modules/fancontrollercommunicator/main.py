# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import json
import logging
import time
from time import sleep

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
)
from fancontrolbridge.modules.fancontrollercommunicator.pyserialadapter import (
    PyserialAdapter,
)
from fancontrolbridge.utils.baseprocess import BaseProcessABC
from fancontrolbridge.utils.component import BaseComponentABC


class main(BaseProcessABC, BaseComponentABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger("fancontrolbridge.modules.serialcommunicator")
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

        command_object = self._send_queue[0]

        try:
            command_object.execute()
            result = command_object.result
            if result is not None:
                self.publish_global_event(result["event"], result["data"])
        except OverflowError:
            self._send_queue.pop(0)
            return
        except UnexpectedResponseError as e:
            message = str(e)
            pass
        except ErrorResponseError as e:
            message = str(e)
            pass
        except ResponseTimeoutError as e:
            message = str(e)
            pass
        else:
            self._send_queue.pop(0)
            self.publish_global_event(
                "controller_command_results",
                {
                    "type": "success",
                    "message": message,
                    "original_command": str(command_object),
                },
            )
            return

        if command_object.tries >= 3:
            self._send_queue.pop(0)
            self.publish_global_event(
                "controller_command_results",
                {
                    "type": "error",
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

                self._send_queue.append(command_object)
        except ValueError:
            self.logger.debug(f"Data is not a dictionary.")
