# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import unittest
import unittest.mock as mock
from multiprocessing import Event, Queue
from unittest.mock import Mock

from src.mqttfancontroller.modules.mqtt import MQTTMessenger
from src.mqttfancontroller.utils.baseprocess import BaseProcessABC
from src.mqttfancontroller.utils.component import BaseComponentABC
from src.mqttfancontroller.utils.observable import Observable


class MQTTMessengerGenericTestCase(unittest.TestCase):
    def setUp(self):
        self.stop_event = Mock(Event)
        self.sub_queue = Mock(Queue)
        self.pub_queue = Mock(Queue)
        self.config = {
            "forwarded_events": list(),
        }

    def test_register_forwarded_events_from_config(self):
        """Forwarded events should be registered as Observers"""
        self.config["forwarded_events"] = [
            {"event": "test1", "topic": "/target/topic1"},
            {"event": "test2", "topic": "/target/topic2"},
            {"event": "test3", "topic": "/target/topic3"},
        ]

        with mock.patch("paho.mqtt.client.Client") as mock_mqtt, mock.patch(
            "mqttfancontroller.utils.baseprocess.Observable"
        ) as mock_events:
            messenger = MQTTMessenger(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )

        for e in self.config["forwarded_events"]:
            mock_events.return_value.register_observer.assert_any_call(
                e["event"], messenger
            )
