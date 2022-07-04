# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

from abc import ABC

from mqttfancontroller.utils.observable import Observer


class BaseComponentABC(Observer):
    config: dict

    def __init__(self, config: dict, **kwargs):
        """Constructor

        Expects config to contain:
            "name" Name of the component
        """
        print("dafuq")
        self.config = config
