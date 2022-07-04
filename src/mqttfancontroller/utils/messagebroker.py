# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import logging
import queue
from abc import ABC, abstractmethod
from dataclasses import dataclass
from multiprocessing import Queue
from time import sleep


@dataclass
class Message:
    sender: int
    data: dict


class MessagingClient:
    """Subscriber for listening to MessageBroker publish queues"""

    def __init__(self, publish_queue: Queue, subscriber_queue: Queue):
        """Constructor

        Arguments:
        publish_queue -- A multiprocessing.Queue in which messages get passed
            to the MessageBroker.
        subscriber_queue -- A multiprocessing.Queue to which messages get
            passed from the MessageBroker.
        """
        # Client ID is to prevent MessageBroker from sending data back
        # to the original sender, since original sender has it already.
        self.client_id = id(subscriber_queue)
        self.subscriber_queue = subscriber_queue
        self.publish_queue = publish_queue

    def fetch_message(self):
        """Tries to get data from the Queue

        Returns data if able, None otherwise. Run periodically to get messages
        one by one.

        Returns:
        A single data blob from the queue if available, None otherwise.
        """
        try:
            if not self.subscriber_queue.empty():
                return self.subscriber_queue.get_nowait()
        except queue.Empty:
            pass  # Empty queue is OK
        return None

    def publish_message(self, data):
        """Send a data blob to be forwarded by the MessageBroker.

        Arguments:
        data -- Any single data blob to be forwarded (a dict perhaps?)
        """
        self.publish_queue.put_nowait(
            Message(
                self.client_id,
                data,
            )
        )


class MessageBroker:
    """Message Broker for interprocess communication

    A broker for passing messages from publish queues to every subscriber queue.

    Methods:
    attach_subscriber -- Attach a subscriber Queue to which we propagate messages.
    detach_subscriber -- Detach a subscriber Queue from the broker.
    get_publish_queue -- Get the publish queue.
    bet_new_subscriber_queue -- Get a new subscriber queue.
    start -- Starts the broker (the primary listening-forwarding loop).
    """

    def __init__(self, stop_event):
        """Constructor

        Creates a single multiprocessing.Queue for sharing between every
        Publisher process.

        Arguments:
        stop_event -- A multiprocessing.Event for gracefully stopping operations
        """
        self._stop_event = stop_event
        self._subscribers = []
        self._publish_queue = Queue()
        self._logger = logging.getLogger("foli-cli.messagebroker.MessageBroker")

    def attach_subscriber(self, subscriber: Queue):
        """Attach a subscriber queue to broker

        Arguments:
        subscriber -- Queue to be added to MessageBroker
        """
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)

    def detach_subscriber(self, subscriber: Queue):
        """Detach a subscriber queue from broker

        Arguments:
        subscriber -- Previously attached Queue
        """
        if subscriber in self._subscribers:
            self._subscribers.remove(subscriber)

    def get_client_queues(self) -> (Queue, Queue):
        """Returns publish and subscriber queues"""
        subscriber_queue = Queue()
        self.attach_subscriber(subscriber_queue)
        return (self._publish_queue, subscriber_queue)

    def start(self):
        """Start the publish-subscribe message transfer loop

        Loops until stop_event Event gets set, passing published message blobs
        one-by-one to every subscriber attached at the time.
        """
        try:
            self._logger.debug("Starting message transfer loop")
            while not self._stop_event.is_set():
                message = self._get_published_message()
                if message is not None:
                    self._forward_message_to_subscribers(message)
                sleep(0.1)
            self._logger.debug("Stopping message transfer loop")
        except KeyboardInterrupt:
            self._logger.debug("Got KeyboardInterrupt")
            self._stop_event.set()

    def _get_published_message(self):
        """Tries to get message from a publisher Queue

        Returns message if able, None otherwise
        """
        try:
            if not self._publish_queue.empty():
                return self._publish_queue.get_nowait()
        except queue.Empty:
            pass  # Empty queue is OK
        return None

    def _forward_message_to_subscribers(self, message: Message):
        """Forwards message blob to every subscriber queue

        Arguments:
        message -- A message blob to be forwarded to subscribers"""
        self._logger.debug(f"Forwarding message")
        for subscriber in self._subscribers:
            # Don't send the message back to the original sender
            if id(subscriber) == message.sender:
                continue
            subscriber.put_nowait(message)
