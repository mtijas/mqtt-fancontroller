# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

from mqttfancontroller.utils.baseprocess import BaseProcessABC
from mqttfancontroller.utils.component import BaseComponentABC
import time


class PrintStdOutput(BaseProcessABC, BaseComponentABC):
    _messages: list = list()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.events.register_observer("*", self)

    def update(self):
        if self._messages:
            print(self._messages.pop())

    def notify(self, event, data):
        self._messages.append(f"{event}: {data}")
