# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import json
import unittest
import unittest.mock as mock
from unittest.mock import Mock
import time

from src.mqttfancontroller.modules.mqttmessenger.main import main
from src.mqttfancontroller.utils.baseprocess import BaseProcessABC
from src.mqttfancontroller.utils.component import BaseComponentABC
from src.mqttfancontroller.utils.observable import Observable


class MQTTMessengerGenericTestCase(unittest.TestCase):
    def setUp(self):
        self.stop_event = Mock()
        self.sub_queue = Mock()
        self.pub_queue = Mock()
        self.config = {
            "publish_events": dict(),
            "subscribe_topics": dict(),
            "host": "",
        }

    def test_register_publish_events_from_config(self):
        """Forwarded events should be registered as Observers"""
        self.config["publish_events"] = {
            "test1": "/target/topic1",
            "test2": "/target/topic2",
            "test3": ["/target/topic3"],  # Both string ans list of strings allowed
        }

        with mock.patch("paho.mqtt.client.Client") as mock_mqtt, mock.patch(
            "mqttfancontroller.utils.baseprocess.Observable"
        ) as mock_events:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )

        for e in self.config["publish_events"]:
            mock_events.return_value.register_observer.assert_any_call(e, messenger)

    def test_nothing_registered_on_empty_forwarded_list(self):
        """No observers should be registered if forwarded events list empty"""
        self.config["publish_events"] = []

        with mock.patch("paho.mqtt.client.Client") as mock_mqtt, mock.patch(
            "mqttfancontroller.utils.baseprocess.Observable"
        ) as mock_events:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )

        mock_events.return_value.register_observer.assert_not_called()

    def test_attribute_error_raised_when_publish_list_missing(self):
        """AttributeError should be raised if publish events list is missing"""
        self.config.pop("publish_events")

        with mock.patch("paho.mqtt.client.Client") as mock_mqtt, mock.patch(
            "mqttfancontroller.utils.baseprocess.Observable"
        ) as mock_events, self.assertRaises(
            AttributeError, msg="publish_events list not found in config"
        ) as raised:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
            # Simulate on_connect callback for successful connection
            mock_mqtt.return_value.on_connect(mock_mqtt, None, {}, 0)

        mock_events.return_value.register_observer.assert_not_called()

    def test_event_not_in_config_should_warn(self):
        """Event not in config should result in WARNING"""
        notify_event = "test-event"
        notify_data = {"This is": "test data"}
        with mock.patch("paho.mqtt.client.Client") as mock_mqtt:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
            # Simulate on_connect callback for successful connection
            mock_mqtt.return_value.on_connect(mock_mqtt, None, {}, 0)

        with self.assertLogs() as cm:
            messenger.notify(notify_event, notify_data)

        self.assertEqual(
            cm.output,
            [
                "WARNING:mqttfancontroller.modules.mqtt:Event 'test-event' not found in MQTT config"
            ],
        )
        mock_mqtt.return_value.publish.assert_not_called()

    def test_object_event_data_passed_json_serialized(self):
        """Event data should be passed to MQTT publish function JSON serialized"""
        notify_event = "test-event"
        notify_data = {"This is": "test data"}
        self.config["publish_events"] = {"test-event": "/target/topic"}
        with mock.patch("paho.mqtt.client.Client") as mock_mqtt:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
            # Simulate on_connect callback for successful connection
            mock_mqtt.return_value.on_connect(mock_mqtt, None, {}, 0)

        messenger.notify(notify_event, notify_data)

        mock_mqtt.return_value.publish.assert_called_once_with(
            self.config["publish_events"]["test-event"], json.dumps(notify_data)
        )

    def test_event_passed_to_publish_function_multiple_topics(self):
        """Event data should be passed to MQTT publish function for every
        topic assigned to an event.
        """
        notify_event = "test-event"
        notify_data = {"This is": "test data"}
        self.config["publish_events"] = {
            "test-event": ["/target/topic", "/target/topic2"],
        }
        with mock.patch("paho.mqtt.client.Client") as mock_mqtt:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
            # Simulate on_connect callback for successful connection
            mock_mqtt.return_value.on_connect(mock_mqtt, None, {}, 0)

        messenger.notify(notify_event, notify_data)

        for topic in self.config["publish_events"]["test-event"]:
            mock_mqtt.return_value.publish.assert_any_call(
                topic, json.dumps(notify_data)
            )

    def test_string_event_data_passed_as_is(self):
        """String event data should be passed as-is"""
        notify_event = "test-event"
        notify_data = "test data"
        self.config["publish_events"] = {"test-event": "/target/topic"}
        with mock.patch("paho.mqtt.client.Client") as mock_mqtt:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
            # Simulate on_connect callback for successful connection
            mock_mqtt.return_value.on_connect(mock_mqtt, None, {}, 0)

        messenger.notify(notify_event, notify_data)

        mock_mqtt.return_value.publish.assert_called_once_with(
            self.config["publish_events"]["test-event"], notify_data
        )

    def test_int_event_data_passed_as_is(self):
        """Int event data should be passed as-is"""
        notify_event = "test-event"
        notify_data = 1
        self.config["publish_events"] = {"test-event": "/target/topic"}
        with mock.patch("paho.mqtt.client.Client") as mock_mqtt:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
            # Simulate on_connect callback for successful connection
            mock_mqtt.return_value.on_connect(mock_mqtt, None, {}, 0)

        messenger.notify(notify_event, notify_data)

        mock_mqtt.return_value.publish.assert_called_once_with(
            self.config["publish_events"]["test-event"], notify_data
        )

    def test_float_event_data_passed_as_is(self):
        """Float event data should be passed as-is"""
        notify_event = "test-event"
        notify_data = 3.1415
        self.config["publish_events"] = {"test-event": "/target/topic"}
        with mock.patch("paho.mqtt.client.Client") as mock_mqtt:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
            # Simulate on_connect callback for successful connection
            mock_mqtt.return_value.on_connect(mock_mqtt, None, {}, 0)

        messenger.notify(notify_event, notify_data)

        mock_mqtt.return_value.publish.assert_called_once_with(
            self.config["publish_events"]["test-event"], notify_data
        )

    def test_attribute_error_raised_when_subscribe_list_missing(self):
        """AttributeError should be raised if subscribe events list is missing"""
        self.config.pop("subscribe_topics")

        with mock.patch("paho.mqtt.client.Client") as mock_mqtt, mock.patch(
            "mqttfancontroller.utils.baseprocess.Observable"
        ) as mock_events, self.assertRaises(
            AttributeError, msg="subscribe_topics list not found in config"
        ) as raised:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
            # Simulate on_connect callback for successful connection
            mock_mqtt.return_value.on_connect(mock_mqtt, None, {}, 0)

    def test_topics_are_subscribed_to_on_connect(self):
        """Topics should be subscribed to on connect"""
        self.config["subscribe_topics"] = [
            "/incoming/topic",
            "/incoming/topic2",
        ]
        with mock.patch("paho.mqtt.client.Client") as mock_mqtt:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
            # Simulate on_connect callback for successful connection
            mock_mqtt.return_value.on_connect(mock_mqtt, None, {}, 0)

        for topic in self.config["subscribe_topics"]:
            mock_mqtt.return_value.subscribe.assert_any_call(topic)

    def test_host_required_in_config(self):
        """Host should exist in connection config"""
        self.config.pop("host")

        with mock.patch("paho.mqtt.client.Client") as mock_mqtt, self.assertRaises(
            AttributeError, msg="host not found in config"
        ) as raised:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )

    def test_autoconnects_only_on_update_and_accepts_host_conf_alone(self):
        """MQTT should get connected on update with host config alone"""
        self.config["host"] = "foo.bar"

        with mock.patch("paho.mqtt.client.Client") as mock_mqtt:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )

        mock_mqtt.return_value.connect.assert_not_called()

        messenger.update()

        mock_mqtt.return_value.connect.assert_called_once_with(
            self.config["host"], 1883, 60, ""
        )

    def test_accepts_port_keepalive_bind_addr_on_connect(self):
        """Port, keepalive and bind_address should be configurable"""
        self.config["host"] = "foo.bar"
        self.config["port"] = 1823
        self.config["keepalive"] = 42
        self.config["bind_address"] = "1.2.3.4"

        with mock.patch("paho.mqtt.client.Client") as mock_mqtt:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )

        messenger.update()

        mock_mqtt.return_value.connect.assert_called_once_with(
            self.config["host"],
            self.config["port"],
            self.config["keepalive"],
            self.config["bind_address"],
        )

    def test_loop_not_called_frequently_after_on_disconnect_callback(self):
        """Loop should not get called too frequently after on_disconnect callback"""
        self.config["host"] = "foo.bar"

        with mock.patch("paho.mqtt.client.Client") as mock_mqtt:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )

        messenger.on_connect(mock_mqtt, None, {}, 0)  # Success
        for i in range(3):
            messenger.update()

        self.assertEqual(mock_mqtt.return_value.loop.call_count, 3)

        messenger.on_disconnect(mock_mqtt, None, 0)  # Clean disconnect

        elapsed = 0.0
        start_time = time.monotonic()
        while elapsed < 0.5:
            messenger.update()
            elapsed = time.monotonic() - start_time
            time.sleep(0.1)

        self.assertEqual(mock_mqtt.return_value.loop.call_count, 4)

    def test_reconnect_interval(self):
        """Reconnect interval should be configurable and working"""
        self.config["reconnect_interval"] = 1

        with mock.patch("paho.mqtt.client.Client") as mock_mqtt:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )

        elapsed = 0.0
        start_time = time.monotonic()
        while elapsed < 2.1:
            messenger.update()
            elapsed = time.monotonic() - start_time
            time.sleep(0.1)

        # Expect 3 calls: one at startup, one at 1 seconds and one at 2 secs.
        self.assertEqual(mock_mqtt.return_value.connect.call_count, 3)

    def test_messages_from_mqtt_get_passed(self):
        """Messages from MQTT topics should get passed"""
        self.config["subscribe_topics"] = [
            "/test/topic",
            "/another/topic",
        ]
        payload = "test-data"
        mock_message = Mock(
            topic="/another/topic", payload=payload.encode(), qos=0, retain=False
        )

        with mock.patch("paho.mqtt.client.Client") as mock_mqtt, mock.patch(
            "mqttfancontroller.utils.baseprocess.Observable"
        ) as mock_events:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )

        messenger.on_message(messenger, None, mock_message)

        mock_events.return_value.notify_observers.assert_any_call(
            "/another/topic", payload
        )
        self.assertEqual(self.pub_queue.put_nowait.call_count, 1)

    def test_messages_from_mqtt_get_passed_test_2(self):
        """Messages from MQTT topics should get passed, test 2"""
        self.config["subscribe_topics"] = [
            "/test/topic/#",
            "/another/topic",
        ]
        payload = "test-data"
        mock_message = Mock(
            topic="/test/topic/subtopic", payload=payload.encode(), qos=0, retain=False
        )

        with mock.patch("paho.mqtt.client.Client") as mock_mqtt, mock.patch(
            "mqttfancontroller.utils.baseprocess.Observable"
        ) as mock_events:
            messenger = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )

        messenger.on_message(messenger, None, mock_message)

        mock_events.return_value.notify_observers.assert_any_call(
            "/test/topic/subtopic", payload
        )
        self.assertEqual(self.pub_queue.put_nowait.call_count, 1)

