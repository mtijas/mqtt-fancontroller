# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

from mqttfancontroller.outputs.base import BaseOutputABC
import time


class PrintStdOutput(BaseOutputABC):
    _event_name: str = "printstreamoutput"
    _messages: list = list()

    def __init__(self, *args):
        super().__init__(*args)
        self.events.register_observer("timestampinput", self)

    def update(self):
        if self._messages:
            print(self._messages.pop())

    def notify(self, event, data):
        self._messages.append(f"{event}: {data}")
