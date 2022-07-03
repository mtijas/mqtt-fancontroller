# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

from mqttfancontroller.inputs.base import BaseInputABC
import time


class TimestampInput(BaseInputABC):
    _event_name: str = "timestampinput"

    def __init__(self, *args):
        super().__init__(*args)
        self.set_update_interval(5)

    def update(self):
        """Get the current unix timestamp"""
        self.logger.debug("TimestampInput update")
        data = {
            "timestamp": time.time()
        }
        self.publish_event(self._event_name, data)
