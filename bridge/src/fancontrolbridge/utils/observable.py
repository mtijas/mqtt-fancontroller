# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

from abc import ABC, abstractmethod


class Observer(ABC):
    """Observer for any Observable"""

    @abstractmethod
    def notify(self, event: str, data):
        """Notify callback for Observable to call on every new notification.

        Arguments:
        event -- The event string Observable.notify_observers() got.
        data -- The data passed with the event. Might be None.
        """
        pass


class Observable:
    """Observable component, to be observed with Observer

    Usage: Inherit or instantiate this, register observers with
    register_observer and fire an event with notify_observers().

    Public methods:
    register_observer -- Register a new Observer
    deregister_observer -- Remove existing Observer registration
    notify_observers -- Notify all Observers registered to particular event.
    """

    def __init__(self):
        self.observers = {"*": []} # Wildcard should always exist

    def register_observer(self, event: str, observer: Observer):
        """Register a new observer to a specific event.

        Arguments:
        event -- A string name of an event (just make something up basically)
            "*" acts as a wildcard: all events will get passed to the observer
        observer -- An Observer object
        """
        if event not in self.observers:
            self.observers[event] = []

        if observer not in self.observers[event]:
            self.observers[event].append(observer)

    def deregister_observer(self, event: str, observer: Observer):
        """Deregister an observer from an event.

        Observer should already be registered in the event.

        Arguments:
        event -- A string name of an event
        observer -- An Observer object already registered in the event

        Raises:
        ValueError if observer not previously registered for the event or if
            already deregistered.
        """
        if observer in self.observers[event]:
            self.observers[event].remove(observer)

    def notify_observers(self, event, data=None):
        """Notify all observers of an event.

        Also has an ability to pass any given data to those observers. Calls
        the .notify method of every observer sequentially, so please don't
        block when handling the call notify gets.

        Arguments:
        event -- A string name of an event
        data -- Any data (a dictionary perhaps?) to be passed to every
            Observer.
        """
        # Pass all events to observers in the star dictionary (wildcard)
        for observer in self.observers["*"]:
            observer.notify(event, data)

        if event not in self.observers or event == "*":
            return

        for observer in self.observers[event]:
            observer.notify(event, data)
