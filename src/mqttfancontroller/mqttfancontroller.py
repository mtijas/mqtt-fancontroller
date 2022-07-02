#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import argparse
from mqttfancontroller.engine import MQTTFanController

def main():
  parser = argparse.ArgumentParser()

  args = parser.parse_args()

  try:
    engine = MQTTFanController()
    engine.shutdown()
  except SystemExit:
    print("Exiting...")
    exit()

if __name__ == '__main__':
  main()
