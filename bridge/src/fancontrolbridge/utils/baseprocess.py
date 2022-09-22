# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import logging
import time
from abc import ABC, abstractmethod
from multiprocessing import current_process
from time import sleep

from fancontrolbridge.utils.messagebroker import MessagingClient
from fancontrolbridge.utils.observable import Observable, Observer


class BaseProcessABC(ABC, MessagingClient):
    _SLEEP_DURATION: float = 0.1

    def __init__(self, config, stop_event, pub_queue, sub_queue, **kwargs):
        self.stop_event = stop_event
        self.logger = logging.getLogger("utils.base.BaseProcessABC")
        MessagingClient.__init__(self, pub_queue, sub_queue)
        self.events = Observable()
        self.config = config

    @abstractmethod
    def update():
        """Update method which gets called once every loop (on start)"""
        pass

    def _loop(self):
        """Called every loop, ensures internal and external tasks are done"""
        self._fetch_events_and_notify_observers()
        self.update()

    def stop(self):
        """Stop gracefully"""
        self.stop_event.set()

    def start(self):
        """Start the main loop"""
        try:
            while not self.stop_event.is_set():
                self._loop()
                sleep(self._SLEEP_DURATION)
        except KeyboardInterrupt:
            self.logger.debug("Got KeyboardInterrupt")
            pass  # It's OK since we would only set stop_event flag here anyway
        finally:
            self.stop()

    def _fetch_events_and_notify_observers(self):
        """Pass events fetched from MessageBroker queue to event observers"""
        message = self.fetch_message()
        if message is not None:
            self.logger.debug(f"Fetched message: {message}")
            self.events.notify_observers(message.data["event"], message.data["data"])

    def publish_global_event(self, event: str, data):
        """Pass an event through messagebroker, and to local observers"""
        self.logger.debug(f"Publishing event: {event} with {data}")
        message_data = {
            "event": event,
            "data": data,
        }
        self.publish_message(message_data)
        self.events.notify_observers(event, data)


class TimedBaseProcessABC(BaseProcessABC):
    _previous_monotonic: float = 0
    _time_elapsed: float = 0
    _update_interval: int = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_update_interval(self.config["update_interval"])

    def set_update_interval(self, interval: int):
        if interval <= 0:
            raise AttributeError("Interval must be over zero")
        self._update_interval = interval

    def _loop(self):
        """Calls update every update_interval seconds"""
        self._fetch_events_and_notify_observers()
        self._time_elapsed += self.get_elapsed_time()
        if self._time_elapsed >= self._update_interval:
            self.logger.debug(f"Elapsed time: {self._time_elapsed}")
            """
            Elapsed time can't just be set to zero since it would mean
            losing the overflow (on slower update cycles). This presets the next
            timer with the time spent over designated duration of a previous timer
            and effectively eliminates update loop creep.
            """
            self._time_elapsed -= self._update_interval
            self.update()

    def start(self):
        """Check for interval value and start main loop"""
        if self._update_interval <= 0:
            raise ValueError("Interval must be over zero")
        self._previous_monotonic = time.monotonic()
        super().start()

    def get_elapsed_time(self):
        """Returns time elapsed since last call"""
        current_m = time.monotonic()
        elapsed = current_m - self._previous_monotonic
        self._previous_monotonic = current_m
        return elapsed
