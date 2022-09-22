# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

from fancontrolbridge.utils.baseprocess import TimedBaseProcessABC
from fancontrolbridge.utils.component import BaseComponentABC
import time


class main(TimedBaseProcessABC, BaseComponentABC):
    def update(self):
        """Get the current unix timestamp"""
        self.logger.debug("TimestampInput update")
        data = {
            "source": self.config["name"],
            "timestamp": time.time()
        }
        self.publish_global_event("timestamp", data)

    def notify(self, event, data):
        """Notification receive callback, not needed but required to exist"""
        self.logger.info(f"TimestampInput got {event} with {data}")
