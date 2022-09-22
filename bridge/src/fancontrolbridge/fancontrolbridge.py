#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import argparse
import logging
import confuse

from fancontrolbridge.engine import Engine


def main():
    logger = setup_logging()

    parser = setup_argparse()
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    config = confuse.Configuration("fancontrolbridge", __name__)
    if args.config is not None:
        try:
            config.set_file(args.config)
        except confuse.exceptions.ConfigReadError as err:
            logger.warning(f"Configuration error: {err}")
    config.set_env()

    logger.debug(f'Initial config: {config}')

    engine = Engine(config, logger)

    try:
        engine.start()
    except KeyboardInterrupt:
        logger.debug("Got KeyboardInterrupt")
    except confuse.exceptions.ConfigError as err:
        logger.warning(f"Configuration error: {err}")
    finally:
        engine.stop()


def setup_logging():
    """Setup global logging
    Returns logger instance
    """
    logger = logging.getLogger("fancontrolbridge")
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
