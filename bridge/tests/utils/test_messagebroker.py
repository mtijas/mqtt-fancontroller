# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import unittest
import unittest.mock as mock
from multiprocessing import Event, Queue
from unittest.mock import Mock

from src.fancontrolbridge.utils.messagebroker import (
    Message,
    MessageBroker,
    MessagingClient,
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
        self.mock_queue.get_nowait.side_effect = [
            Message(1, {1}),
            Message(2, {2}),
            Message(3, {3}),
        ]
        self.mock_queue.empty.side_effect = [False, False, False, True]
        self.broker._publish_queue = self.mock_queue

        self.clients = []
        for i in range(self.subscriber_count):
            self.clients.append(Mock())

    def test_attach_subscribers(self):
        """Clients should be able to be attached"""
        for client in self.clients:
            self.broker.attach_subscriber(client)

        for client in self.clients:
            self.assertIn(client, self.broker._subscribers)

    def test_detach_subscribers(self):
        """Clients should be able to be detached"""
        for client in self.clients:
            self.broker.attach_subscriber(client)

        self.broker.detach_subscriber(self.clients[0])

        self.assertNotIn(self.clients[0], self.broker._subscribers)

    def test_message_passing(self):
        """Test message passing from publish queue to subscribe queues"""
        for client in self.clients:
            self.broker.attach_subscriber(client)

        self.broker.start()

        for client in self.clients:
            self.assertEqual(3, client.put_nowait.call_count)

    @mock.patch("multiprocessing.Queue")
    def test_getting_queues(self, mock_queue):
        """Subscriber queue should be added and returned"""
        (pub_q, sub_q) = self.broker.get_client_queues()

        self.assertIn(sub_q, self.broker._subscribers)
        self.assertEqual(pub_q, self.mock_queue)
