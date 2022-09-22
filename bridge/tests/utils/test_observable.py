# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import Mock

from src.fancontrolbridge.utils.observable import Observable


class TestObservable(unittest.TestCase):
    def setUp(self):
        self.observer_count = 10
        self.observable = Observable()
        self.dummy_observers = []
        for i in range(self.observer_count):
            self.dummy_observers.append(Mock())

    def test_register_observers(self):
        """Observers should be able to be added to observable events"""
        for i in range(self.observer_count):
            self.observable.register_observer(f"event-{i}", self.dummy_observers[0])

        for i in range(self.observer_count):
            event_observers = self.observable.observers[f"event-{i}"]
            self.assertIn(self.dummy_observers[0], event_observers)

    def test_register_multiple_observers_single_event(self):
        """Multiple Observers should be able to be added to a single event"""
        for dummy in self.dummy_observers:
            self.observable.register_observer("event-single", dummy)

        event_observers = self.observable.observers["event-single"]
        for i in range(self.observer_count):
            self.assertIn(self.dummy_observers[i], event_observers)

    def test_observer_not_allowed_multiple_times_on_event(self):
        """Single observer should not be allowed to register multiple times
        to single event"""
        for i in range(3):
            self.observable.register_observer("multi-test-1", self.dummy_observers[0])

        self.assertEqual(len(self.observable.observers["multi-test-1"]), 1)

    def test_deregister_observer_from_single_event(self):
        """Single observer should be able to be deregistered"""
        for dummy in self.dummy_observers:
            self.observable.register_observer("deregister-1", dummy)
            self.observable.register_observer("deregister-2", dummy)

        self.observable.deregister_observer("deregister-1", self.dummy_observers[0])

        event_observers_1 = self.observable.observers["deregister-1"]
        event_observers_2 = self.observable.observers["deregister-2"]
        self.assertNotIn(self.dummy_observers[0], event_observers_1)
        self.assertIn(self.dummy_observers[0], event_observers_2)

    def test_deregister_already_deregistered_observer_does_nothing(self):
        """Deregistering already deregistered observer does nothing"""
        for dummy in self.dummy_observers:
            self.observable.register_observer("deregister", dummy)

        self.observable.deregister_observer("deregister", self.dummy_observers[1])
        self.observable.deregister_observer("deregister", self.dummy_observers[1])

        event_observers = self.observable.observers["deregister"]
        self.assertNotIn(self.dummy_observers[1], event_observers)

    def test_notifying_all_observers_without_data(self):
        """All observers should be notified on single call without data"""
        for dummy in self.dummy_observers:
            self.observable.register_observer("notify", dummy)

        self.observable.notify_observers("notify")

        for dummy in self.dummy_observers:
            dummy.notify.assert_called_once_with("notify", None)

    def test_notifying_all_observers_with_data(self):
        """All observers should be notified on single call with data"""
        data = {"type": "message"}
        for dummy in self.dummy_observers:
            self.observable.register_observer("notify", dummy)

        self.observable.notify_observers("notify", data)

        for dummy in self.dummy_observers:
            dummy.notify.assert_called_once_with("notify", data)

    def test_not_notifying_on_unregistered_events(self):
        """Observers should not be notified on event not registered to"""
        for dummy in self.dummy_observers:
            self.observable.register_observer("notify", dummy)

        self.observable.notify_observers("nonexisting")

        for dummy in self.dummy_observers:
            dummy.notify.assert_not_called()
