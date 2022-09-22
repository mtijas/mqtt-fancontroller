# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import json
import time
import unittest
import unittest.mock as mock
from unittest.mock import Mock

from src.fancontrolbridge.modules.fancontrollercommunicator.main import (
    main,
)
from src.fancontrolbridge.modules.fancontrollercommunicator.errors import (
    ErrorResponseError,
    ResponseTimeoutError,
    UnexpectedResponseError,
)
from src.fancontrolbridge.utils.baseprocess import BaseProcessABC
from src.fancontrolbridge.utils.component import BaseComponentABC
from src.fancontrolbridge.utils.observable import Observable


class FanControllerCommunicatorTestCase(unittest.TestCase):
    def setUp(self):
        self.stop_event = Mock()
        self.sub_queue = Mock()
        self.pub_queue = Mock()
        self.config = {
            "command_topic": "fancontrolbridge/test/command",
            "report_interval": 15,
            "port": "dummy",
            "bauds": 9600,
        }
        self.commands = {
            "HELLO": 1,
            "ACK": 2,
            "RCVD": 3,
            "END": 6,
            "ERROR": 7,
            "SET_TARGET": 64,
            "SET_OUTPUT": 65,
            "SET_KP": 66,
            "SET_KI": 67,
            "SET_KD": 68,
            "SET_MODE": 69,
            "GET_STATUS": 70,
            "GET_SETTINGS": 71,
        }

    def test_serial_initialized_with_correct_config(self):
        """Serial lib should be initialized with values from config"""
        with mock.patch("serial.Serial") as mock_serial, mock.patch(
            "fancontrolbridge.utils.baseprocess.Observable"
        ) as mock_events:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )

        mock_serial.assert_called_once_with(
            self.config["port"], self.config["bauds"], timeout=5
        )
        mock_events.return_value.register_observer.assert_called_once_with(
            self.config["command_topic"], comms
        )

    def test_unexpected_response_to_hello_prevents_sending_further_data(self):
        """No data should be sent if HELLO fails"""
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ERROR"].to_bytes(1, "little"),
        ]

        comms.notify("dummy", {"command": "SET_TARGET", "channel": 1, "value": 42})
        comms.update()

        self.assertEqual(mock_serial.return_value.read.call_count, 1)
        self.assertEqual(mock_serial.return_value.write.call_count, 1)
        mock_serial.return_value.write.assert_called_once_with(
            self.commands["HELLO"].to_bytes(1, "little")
        )

    def test_sending_message_is_tried_three_times_if_hello_fails(self):
        """Sending message should be retried twice in case of errors"""
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ERROR"].to_bytes(1, "little"),
            self.commands["ERROR"].to_bytes(1, "little"),
            self.commands["ERROR"].to_bytes(1, "little"),
            self.commands["ERROR"].to_bytes(1, "little"),
            self.commands["ERROR"].to_bytes(1, "little"),
        ]

        comms.notify("dummy", {"command": "SET_TARGET", "channel": 1, "value": 42})
        for i in range(5):
            comms.update()

        self.assertEqual(mock_serial.return_value.read.call_count, 3)
        self.assertEqual(mock_serial.return_value.write.call_count, 3)
        mock_serial.return_value.write.assert_has_calls(
            [
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
            ]
        )

    def test_failing_send_message_is_tried_three_times_total(self):
        """Sending message should be retried twice in case of errors, test 2"""
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ACK"].to_bytes(1, "little"),
            self.commands["ERROR"].to_bytes(1, "little"),
            self.commands["ACK"].to_bytes(1, "little"),
            self.commands["ERROR"].to_bytes(1, "little"),
            self.commands["ACK"].to_bytes(1, "little"),
            self.commands["ERROR"].to_bytes(1, "little"),
        ]

        comms.notify("dummy", {"command": "SET_TARGET", "channel": 1, "value": 42})
        for i in range(5):
            comms.update()

        self.assertEqual(mock_serial.return_value.read.call_count, 6)
        self.assertEqual(mock_serial.return_value.write.call_count, 12)
        mock_serial.return_value.write.assert_has_calls(
            [
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["SET_TARGET"].to_bytes(1, "little")),
                mock.call((1).to_bytes(1, "little")),
                mock.call((420).to_bytes(2, "little")),
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["SET_TARGET"].to_bytes(1, "little")),
                mock.call((1).to_bytes(1, "little")),
                mock.call((420).to_bytes(2, "little")),
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["SET_TARGET"].to_bytes(1, "little")),
                mock.call((1).to_bytes(1, "little")),
                mock.call((420).to_bytes(2, "little")),
            ]
        )

    def test_set_target(self):
        """SET_TARGET command should send HELLO, command and value to serial"""
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ACK"].to_bytes(1, "little"),
            self.commands["RCVD"].to_bytes(1, "little"),
        ]

        comms.notify("dummy", {"command": "SET_TARGET", "channel": 1, "value": 42})
        comms.update()

        self.assertEqual(mock_serial.return_value.read.call_count, 2)
        self.assertEqual(mock_serial.return_value.write.call_count, 4)
        mock_serial.return_value.write.assert_has_calls(
            [
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["SET_TARGET"].to_bytes(1, "little")),
                mock.call((1).to_bytes(1, "little")),
                mock.call((420).to_bytes(2, "little")),
            ]
        )

    def test_set_target_cut_to_one_decimal(self):
        """SET_TARGET command should cut value to one decimal"""
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ACK"].to_bytes(1, "little"),
            self.commands["RCVD"].to_bytes(1, "little"),
        ]

        comms.notify("dummy", {"command": "SET_TARGET", "channel": 1, "value": 422.56})
        comms.update()

        self.assertEqual(mock_serial.return_value.read.call_count, 2)
        self.assertEqual(mock_serial.return_value.write.call_count, 4)
        mock_serial.return_value.write.assert_has_calls(
            [
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["SET_TARGET"].to_bytes(1, "little")),
                mock.call((1).to_bytes(1, "little")),
                mock.call((4225).to_bytes(2, "little")),
            ]
        )

    def test_set_output(self):
        """SET_OUTPUT command should send HELLO, command and value to serial"""
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ACK"].to_bytes(1, "little"),
            self.commands["RCVD"].to_bytes(1, "little"),
        ]

        comms.notify("dummy", {"command": "SET_OUTPUT", "channel": 1, "value": 255})
        comms.update()

        self.assertEqual(mock_serial.return_value.read.call_count, 2)
        self.assertEqual(mock_serial.return_value.write.call_count, 4)
        mock_serial.return_value.write.assert_has_calls(
            [
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["SET_OUTPUT"].to_bytes(1, "little")),
                mock.call((1).to_bytes(1, "little")),
                mock.call((255).to_bytes(1, "little")),
            ]
        )

    def test_set_kp(self):
        """SET_KP command should send HELLO, command and value to serial"""
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ACK"].to_bytes(1, "little"),
            self.commands["RCVD"].to_bytes(1, "little"),
        ]

        comms.notify("dummy", {"command": "SET_KP", "channel": 1, "value": 20.42})
        comms.update()

        self.assertEqual(mock_serial.return_value.read.call_count, 2)
        self.assertEqual(mock_serial.return_value.write.call_count, 4)
        mock_serial.return_value.write.assert_has_calls(
            [
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["SET_KP"].to_bytes(1, "little")),
                mock.call((1).to_bytes(1, "little")),
                mock.call((2042).to_bytes(2, "little")),
            ]
        )

    def test_set_kp_value_cut_to_two_decimals(self):
        """SET_KP command should cut value to 2 decimals"""
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ACK"].to_bytes(1, "little"),
            self.commands["RCVD"].to_bytes(1, "little"),
        ]

        comms.notify("dummy", {"command": "SET_KP", "channel": 1, "value": 203.4298})
        comms.update()

        self.assertEqual(mock_serial.return_value.read.call_count, 2)
        self.assertEqual(mock_serial.return_value.write.call_count, 4)
        mock_serial.return_value.write.assert_has_calls(
            [
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["SET_KP"].to_bytes(1, "little")),
                mock.call((1).to_bytes(1, "little")),
                mock.call((20342).to_bytes(2, "little")),
            ]
        )

    def test_set_ki(self):
        """SET_KI command should send HELLO, command and value to serial"""
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ACK"].to_bytes(1, "little"),
            self.commands["RCVD"].to_bytes(1, "little"),
        ]

        comms.notify("dummy", {"command": "SET_KI", "channel": 1, "value": 20.42})
        comms.update()

        self.assertEqual(mock_serial.return_value.read.call_count, 2)
        self.assertEqual(mock_serial.return_value.write.call_count, 4)
        mock_serial.return_value.write.assert_has_calls(
            [
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["SET_KI"].to_bytes(1, "little")),
                mock.call((1).to_bytes(1, "little")),
                mock.call((2042).to_bytes(2, "little")),
            ]
        )

    def test_set_ki_value_cut_to_two_decimals(self):
        """SET_KI command should cut value to 2 decimals"""
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ACK"].to_bytes(1, "little"),
            self.commands["RCVD"].to_bytes(1, "little"),
        ]

        comms.notify("dummy", {"command": "SET_KI", "channel": 1, "value": 203.4298})
        comms.update()

        self.assertEqual(mock_serial.return_value.read.call_count, 2)
        self.assertEqual(mock_serial.return_value.write.call_count, 4)
        mock_serial.return_value.write.assert_has_calls(
            [
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["SET_KI"].to_bytes(1, "little")),
                mock.call((1).to_bytes(1, "little")),
                mock.call((20342).to_bytes(2, "little")),
            ]
        )

    def test_set_kd(self):
        """SET_KD command should send HELLO, command and value to serial"""
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ACK"].to_bytes(1, "little"),
            self.commands["RCVD"].to_bytes(1, "little"),
        ]

        comms.notify("dummy", {"command": "SET_KD", "channel": 1, "value": 20.42})
        comms.update()

        self.assertEqual(mock_serial.return_value.read.call_count, 2)
        self.assertEqual(mock_serial.return_value.write.call_count, 4)
        mock_serial.return_value.write.assert_has_calls(
            [
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["SET_KD"].to_bytes(1, "little")),
                mock.call((1).to_bytes(1, "little")),
                mock.call((2042).to_bytes(2, "little")),
            ]
        )

    def test_set_kd_value_cut_to_two_decimals(self):
        """SET_KD command should cut value to 2 decimals"""
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ACK"].to_bytes(1, "little"),
            self.commands["RCVD"].to_bytes(1, "little"),
        ]

        comms.notify("dummy", {"command": "SET_KD", "channel": 1, "value": 203.4298})
        comms.update()

        self.assertEqual(mock_serial.return_value.read.call_count, 2)
        self.assertEqual(mock_serial.return_value.write.call_count, 4)
        mock_serial.return_value.write.assert_has_calls(
            [
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["SET_KD"].to_bytes(1, "little")),
                mock.call((1).to_bytes(1, "little")),
                mock.call((20342).to_bytes(2, "little")),
            ]
        )

    def test_set_mode(self):
        """SET_MODE command should send HELLO, command and value to serial"""
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ACK"].to_bytes(1, "little"),
            self.commands["RCVD"].to_bytes(1, "little"),
        ]

        comms.notify("dummy", {"command": "SET_MODE", "channel": 1, "value": 1})
        comms.update()

        self.assertEqual(mock_serial.return_value.read.call_count, 2)
        self.assertEqual(mock_serial.return_value.write.call_count, 4)
        mock_serial.return_value.write.assert_has_calls(
            [
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["SET_MODE"].to_bytes(1, "little")),
                mock.call((1).to_bytes(1, "little")),
                mock.call((1).to_bytes(1, "little")),
            ]
        )

    def test_get_status_comms_with_bridge(self):
        """GET_STATUS should send HELLO and command, expect 8 bytes and
        respond with RCVD"""
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ACK"].to_bytes(1, "little"),
            (300 + 32768).to_bytes(2, "little"),
            (315 + 32768).to_bytes(2, "little"),
            (7500 + 32768).to_bytes(2, "little"),
            (42 + 32768).to_bytes(2, "little"),
        ]

        comms.notify("dummy", {"command": "GET_STATUS", "channel": 1})
        comms.update()

        self.assertEqual(mock_serial.return_value.read.call_count, 5)
        self.assertEqual(mock_serial.return_value.write.call_count, 4)
        mock_serial.return_value.write.assert_has_calls(
            [
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["GET_STATUS"].to_bytes(1, "little")),
                mock.call((1).to_bytes(1, "little")),
                mock.call(self.commands["RCVD"].to_bytes(1, "little")),
            ]
        )

    def test_get_status_forwards_received_message_to_bus(self):
        """GET_STATUS should forward received message to message bus"""
        publish_mock = Mock()
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ACK"].to_bytes(1, "little"),
            (300 + 32768).to_bytes(2, "little"),
            (315 + 32768).to_bytes(2, "little"),
            (7500 + 32768).to_bytes(2, "little"),
            (42 + 32768).to_bytes(2, "little"),
        ]
        comms.publish_global_event = publish_mock

        comms.notify("dummy", {"command": "GET_STATUS", "channel": 1})
        comms.update()

        publish_mock.assert_called_once_with(
            "controller_status",
            {
                "channel": 1,
                "temp": 30.0,
                "target": 31.5,
                "speed": 7500,
                "output": 42,
            },
        )

    def test_get_settings_comms_with_bridge(self):
        """GET_SETTINGS should send HELLO and command, expect 8 bytes and
        respond with RCVD"""
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ACK"].to_bytes(1, "little"),
            (2).to_bytes(2, "little"),
            (315).to_bytes(2, "little"),
            (7500).to_bytes(2, "little"),
            (42).to_bytes(2, "little"),
        ]

        comms.notify("dummy", {"command": "GET_SETTINGS", "channel": 1})
        comms.update()

        self.assertEqual(mock_serial.return_value.read.call_count, 5)
        self.assertEqual(mock_serial.return_value.write.call_count, 4)
        mock_serial.return_value.write.assert_has_calls(
            [
                mock.call(self.commands["HELLO"].to_bytes(1, "little")),
                mock.call(self.commands["GET_SETTINGS"].to_bytes(1, "little")),
                mock.call((1).to_bytes(1, "little")),
                mock.call(self.commands["RCVD"].to_bytes(1, "little")),
            ]
        )

    def test_get_settings_forwards_received_message_to_bus(self):
        """GET_SETTINGS should forward received message to message bus"""
        publish_mock = Mock()
        with mock.patch("serial.Serial") as mock_serial:
            comms = main(
                config=self.config,
                stop_event=self.stop_event,
                pub_queue=self.pub_queue,
                sub_queue=self.sub_queue,
            )
        mock_serial.return_value.read.side_effect = [
            self.commands["ACK"].to_bytes(1, "little"),
            (2).to_bytes(2, "little"),
            (315).to_bytes(2, "little"),
            (7500).to_bytes(2, "little"),
            (42).to_bytes(2, "little"),
        ]
        comms.publish_global_event = publish_mock

        comms.notify("dummy", {"command": "GET_SETTINGS", "channel": 1})
        comms.update()

        publish_mock.assert_called_once_with(
            "controller_settings",
            {
                "channel": 1,
                "mode": 2,
                "kp": 3.15,
                "ki": 75.00,
                "kd": 0.42,
            },
        )
