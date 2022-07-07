# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import paho.mqtt.client as mqtt

from mqttfancontroller.utils.baseprocess import BaseProcessABC
from mqttfancontroller.utils.component import BaseComponentABC


class MQTTMessenger(BaseProcessABC, BaseComponentABC):
    _client: mqtt.Client

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = mqtt.Client()

        if "forwarded_events" not in self.config:
            raise AttributeError("forwarded_events list not found in config")

        for forwarded in self.config["forwarded_events"]:
            self.events.register_observer(forwarded["event"], self)

    def update(self):
        if self._messages:
            print(self._messages.pop())

    def notify(self, event, data):
        pass
