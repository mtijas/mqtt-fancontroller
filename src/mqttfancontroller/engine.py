# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only


class Engine:
    def __init__(self, config):
        self.config = config
        print("Engine started!")

    def shutdown(self):
        """Shut down engine gracefully"""
        print("Engine stopping...")
        print("...stopped!")
