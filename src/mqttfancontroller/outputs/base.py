# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

from abc import ABC

from mqttfancontroller.utils.baseprocess import BaseProcessABC
from mqttfancontroller.utils.message import Message
from mqttfancontroller.utils.observable import Observer


class BaseOutputABC(BaseProcessABC, Observer):
    _event_name: str = "output"
    _source: str

    def __init__(self, name: str, *args):
        super().__init__(*args)
        self._source = name

    def publish_event(self, event: str, data: dict):
        """Publish an event through messagebroker as Message"""
        data["source"] = self._source
        super().publish_event(event, data)
