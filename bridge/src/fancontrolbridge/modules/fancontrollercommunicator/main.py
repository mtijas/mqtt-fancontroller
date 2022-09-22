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

        command_object = self._send_queue[0]

        try:
            command_object.execute()
            result = command_object.result
            if result is not None:
                self.publish_global_event(result["event"], result["data"])
        except OverflowError:
            self._send_queue.pop(0)
            return
        except UnexpectedResponseError:
            pass
        except ErrorResponseError:
            pass
        except ResponseTimeoutError:
            pass
        else:
            self._send_queue.pop(0)
            return

        if command_object.tries >= 3:
            self._send_queue.pop(0)

    def notify(self, event, data):
        """Generates command objects from event data.

        Expects data to be a dict containing "command" and "channel".
        Might also contain "value" (mandatory for SET_* commands, not used
        in GET_* commands)
        """
        if type(data) is not dict:
            return

        if "command" not in data or "channel" not in data:
            return

        if data["command"] in self._commands.keys():
            command_object = self._commands[data["command"]](self._serial_adapter)
            command_object.set_channel(data["channel"])

            if "value" in data:
                command_object.set_value(data["value"])

            self._send_queue.append(command_object)
