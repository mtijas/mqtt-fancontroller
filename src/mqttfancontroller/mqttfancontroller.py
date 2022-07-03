#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import argparse
import logging

from mqttfancontroller.config import Config
from mqttfancontroller.engine import Engine


def main():
    logger = setup_logging()

    parser = setup_argparse()
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    config = Config("mqttfancontroller", logger, args.config)
    engine = Engine(config, logger)
    engine.start()


def setup_logging():
    """Setup global logging
    Returns logger instance
    """
    logger = logging.getLogger("mqttfancontroller")
    logger.setLevel(logging.WARNING)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(name)s [%(levelname)s]: %(message)s"))

    logger.addHandler(handler)

    return logger


def setup_argparse():
    """Setup Argument Parser"""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c",
        "--config",
        dest="config",
        help="Load a custom configuration file",
        default=None,
    )
    parser.add_argument(
        "-d", "--debug", dest="debug", help="Enable debug messages", action="store_true"
    )

    return parser


if __name__ == "__main__":
    main()
