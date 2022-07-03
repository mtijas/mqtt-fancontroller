# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

from multiprocessing import Queue, Event
import unittest
from unittest.mock import Mock
import unittest.mock as mock

from src.mqttfancontroller.utils.messagebroker import (
    MessageBroker,
    Publisher,
    Subscriber,
)


class TestMessageBroker(unittest.TestCase):
    @mock.patch("multiprocessing.Event")
    def setUp(self, mock_event):
        self.subscriber_count = 10
        self.publisher_count = 10
        self.stop_event = mock_event
        # Stop message broker after fifth round
        self.stop_event.is_set.side_effect = [False, False, False, False, True]
        self.broker = MessageBroker(self.stop_event)

        self.mock_queue = Mock()
        self.mock_queue.get_nowait.side_effect = [{1}, {2}, {3}]
        self.mock_queue.empty.side_effect = [False, False, False, True]
        self.broker._publish_queue = self.mock_queue

        self.subscriber_queues = []
        for i in range(self.subscriber_count):
            self.subscriber_queues.append(Mock())

    def test_attach_subscriber_queues(self):
        """Subscriber queues should be able to be attached"""
        for q in self.subscriber_queues:
            self.broker.attach_subscriber(q)

        for q in self.subscriber_queues:
            self.assertIn(q, self.broker._subscribers)

    def test_detach_subscriber_queues(self):
        """Subscriber queues should be able to be detached"""
        for q in self.subscriber_queues:
            self.broker.attach_subscriber(q)

        self.broker.detach_subscriber(self.subscriber_queues[0])

        self.assertNotIn(self.subscriber_queues[0], self.broker._subscribers)

    def test_message_passing(self):
        """Test message passing from publish queue to subscribe queues"""
        for q in self.subscriber_queues:
            self.broker.attach_subscriber(q)

        self.broker.start()

        for q in self.subscriber_queues:
            self.assertEqual(3, q.put_nowait.call_count)

    def test_getting_subscriber_queue(self):
        """Subscriber queue should be added and returned"""
        result = self.broker.get_new_subscriber_queue()

        self.assertIn(result, self.broker._subscribers)

    def test_getting_publisher_queue(self):
        """Publisher queue should be proper"""
        result = self.broker.get_publish_queue()

        self.assertEqual(result, self.mock_queue)
