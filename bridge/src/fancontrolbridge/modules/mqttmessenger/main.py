# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import json
import logging
import time
from enum import Enum
import socket

import paho.mqtt.client as mqtt
from fancontrolbridge.utils.baseprocess import BaseProcessABC
from fancontrolbridge.utils.component import BaseComponentABC


class Status(Enum):
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2


class main(BaseProcessABC, BaseComponentABC):
    _client: mqtt.Client
    _queued_messages: list
    _reconnect_interval: int
    _time_since_last_connection_attempt: float
    _previous_connection_attempt_at: float
    _connect_tries_count: int
    _status: Status

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(
            "fancontrolbridge.modules.mqttmessenger")
        self._client = mqtt.Client()
        self._reconnect_interval = 30
        self._previous_connect_call_at = 0.0
        self._connect_tries_count = 0
        self._status = Status.DISCONNECTED

        if "host" not in self.config:
            raise AttributeError("host not found in config")

        if "reconnect_interval" in self.config:
            self._reconnect_interval = self.config["reconnect_interval"]

        if "username" in self.config:
            username = self.config["username"]
            password = None
            if "password" in self.config:
                password = self.config["password"]
            self.logger.debug(
                f"Set MQTT credentials: {username} and {password}")
            self._client.username_pw_set(username, password)

        self._client.on_connect = self.on_connect
        self._client.on_disconnect = self.on_disconnect
        self._client.on_message = self.on_message
        self._client.on_subscribe = self.on_subscribe

        self._register_publish_events()

    def update(self):
        """Process loop"""
        if self._status != Status.CONNECTED and self._has_reconnect_interval_passed():
            self.logger.debug("Reconnecting...")
            self._client.disconnect()
            self._client.loop(timeout=2)
            self._connect()

        if self._status != Status.DISCONNECTED:
            self._client.loop(timeout=0.1)

    def notify(self, event, data):
        """Publishes event data to MQTT topic.

        Int, float and string data is passed as-is, others get serialized
        to JSON
        """
        if event not in self.config["publish_events"]:
            self.logger.warning(f"Event '{event}' not found in MQTT config")
            return  # It's OK, we do not want to crash here so no Exceptions

        if (
            not isinstance(data, int)
            and not isinstance(data, float)
            and not isinstance(data, str)
        ):
            data = json.dumps(data)

        topic = self.config["publish_events"][event]
        if isinstance(topic, list):
            for single in topic:
                message_info = self._client.publish(single, data)
        else:
            message_info = self._client.publish(topic, data)

    def stop(self):
        """Ensure messages get delivered before stopping"""
        if self._status == Status.DISCONNECTED:
            # Assume everything is OK if already disconnected
            super().stop()
            return

        self.logger.info("Stopping MQTT, please wait...")
        self._client.loop(timeout=5)
        self._client.disconnect()
        super().stop()

    def on_connect(self, client, userdata, flags, rc):
        """On connect callback"""
        if (rc > 0):
            self.logger.warning(f"Connection error {rc}")
            self._status = Status.DISCONNECTED
            return

        self.logger.debug(f"Connected to broker with status {rc}")
        self._connect_tries_count = 0
        self._status = Status.CONNECTED
        self._subscribe_to_topics()

    def on_disconnect(self, client, userdata, rc):
        """On disconnect callback"""
        self._status = Status.DISCONNECTED
        if rc == 0:
            self.logger.debug(f"Expected disconnect successful.")
        else:
            self.logger.warning("Unexpected disconnect.")

    def on_message(self, client, userdata, message):
        """On message callback"""
        self.publish_global_event(message.topic, message.payload.decode())

    def on_subscribe(self, client, userdata, mid, granted_qos):
        """On subscrive callback"""
        self.logger.debug(f"Subscribed with mid {mid}")

    def _connect(self):
        """Try to establish connection to MQTT broker"""
        self.logger.debug(f"Connecting to broker {self.config['host']}")
        self._previous_connect_call_at = time.monotonic()
        self._status = Status.CONNECTING
        self._connect_tries_count += 1
        port = 1883
        keepalive = 60
        bind_address = ""

        if "port" in self.config:
            port = self.config["port"]
        if "keepalive" in self.config:
            keepalive = self.config["keepalive"]
        if "bind_address" in self.config:
            bind_address = self.config["bind_address"]

        try:
            self._client.connect(
                self.config["host"], port, keepalive, bind_address
            )
        except socket.error as e:
            self.logger.critical(f"Client exception {e}")
            self._status = Status.DISCONNECTED

    def _register_publish_events(self):
        """Register Observers from config"""
        if "publish_events" not in self.config:
            raise AttributeError("publish_events list not found in config")

        for forwarded in self.config["publish_events"]:
            self.events.register_observer(forwarded, self)

    def _subscribe_to_topics(self):
        """Subscribe to topics for passing MQTT data as events"""
        if "subscribe_topics" not in self.config:
            raise AttributeError("subscribe_topics list not found in config")

        for topic in self.config["subscribe_topics"]:
            self.logger.debug(f"Subscribing to topic {topic}")
            self._client.subscribe(topic)

    def _has_reconnect_interval_passed(self):
        """Returns true if enough time has passed from previous connect"""
        time_since_last_connect = time.monotonic() - self._previous_connect_call_at
        return time_since_last_connect > self._reconnect_interval
