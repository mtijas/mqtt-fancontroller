#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

class MQTTFanController():
  def __init__(self):
    print("Engine started!")

  def shutdown(self):
    """Shut down engine gracefully"""
    print("Engine stopping...")
    print("...stopped!")

