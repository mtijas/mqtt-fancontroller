# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import logging
import queue
from abc import ABC, abstractmethod
from multiprocessing import Queue
from time import sleep


class Subscriber:
    """Subscriber for listening to MessageBroker publish queues"""

    def __init__(self, queue):
        """Constructor

        Arguments:
        queue -- A multiprocessing.Queue in which messages get passed from the
            MessageBroker.
        """
        self.receive_queue = queue

    def fetch_message(self):
        """Tries to get data from the Queue

        Returns data if able, None otherwise. Run periodically to get messages
        one by one.

        Returns:
        A single data blob from the queue if available, None otherwise.
        """
        try:
            if not self.receive_queue.empty():
                return self.receive_queue.get_nowait()
        except queue.Empty:
            pass  # Empty queue is OK
        return None


class Publisher:
    """Publisher for publishing interprocess messages through MessageBroker"""

    def __init__(self, queue):
        """Constructor

        Arguments:
        queue -- A multiprocessing.Queue in which messages get passed to the
            MessageBroker. Fetch this from MessageBroker.get_publish_queue().
        """
        self.publish_queue = queue

    def publish_message(self, data):
        """Publish a data blob to be forwarded by the MessageBroker.

        Arguments:
        data -- Any single data blob to be forwarded (a dict perhaps?)
        """
        self.publish_queue.put_nowait(data)


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

    def get_publish_queue(self) -> Queue:
        """Returns publish queue"""
        return self._publish_queue

    def get_new_subscriber_queue(self) -> Queue:
        """Creates a new subscriber queue, attachs it and returns it"""
        queue = Queue()
        self.attach_subscriber(queue)
        return queue

    def start(self):
        """Start the publish-subscribe message transfer loop

        Loops until stop_event Event gets set, passing published data blobs
        one-by-one to every subscriber attached at the time.
        """
        try:
            self._logger.debug("Starting message transfer loop")
            while not self._stop_event.is_set():
                data = self._get_published_data()
                if data is not None:
                    self._forward_data_to_subscribers(data)
                sleep(0.1)
            self._logger.debug("Stopping message transfer loop")
        except KeyboardInterrupt:
            self._logger.debug("Got KeyboardInterrupt")
            self._stop_event.set()

    def _get_published_data(self):
        """Tries to get data from a publisher Queue

        Returns data if able, None otherwise
        """
        try:
            if not self._publish_queue.empty():
                return self._publish_queue.get_nowait()
        except queue.Empty:
            pass  # Empty queue is OK
        return None

    def _forward_data_to_subscribers(self, data):
        """Forwards data blob to every subscriber queue

        Arguments:
        data -- A data blob to be forwarded to subscribers"""
        self._logger.debug(f"Forwarding data")
        for subscriber in self._subscribers:
            subscriber.put_nowait(data)
