#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import argparse
from mqttfancontroller.engine import Engine
from mqttfancontroller.config import Config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", dest="config", help="Load a custom configuration file"
    )
    parser.set_defaults(config=None)
    args = parser.parse_args()

    try:
        config = Config(args.config)
        engine = Engine(config)
    except SystemExit:
        print("Exiting...")
        exit()


if __name__ == "__main__":
    main()
