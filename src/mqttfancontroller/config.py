# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

import configparser
from pathlib import Path

from appdirs import AppDirs


class Config:
    def __enter__(self):
        return self.parser

    def __exit__(self, type, value, traceback):
        pass

    def __init__(self, app_name: str, config_file: str = None):
        self.app_name = app_name
        self.parser = configparser.ConfigParser()
        self._possible_files = [
            f"~/.config/{self.app_name}/config.ini",
            f"~/.{self.app_name}-config.ini",
        ]

        if config_file is not None:
            self._possible_files.insert(0, config_file)
        self.insert_xdg_conf_location()

        self._selected_config = self.find_config()

        if self._selected_config is not None:
            self.parser.read(self._selected_config)

    def insert_xdg_conf_location(self):
        """Insert XDG config file location"""
        dirs = AppDirs(f"{self.app_name}")
        xdg_config = dirs.user_config_dir
        p = Path(xdg_config).joinpath("config.ini")
        self._possible_files.insert(1, str(p))

    def find_config(self):
        """Try to find config file"""
        for possibility in self._possible_files:
            p = Path(possibility)
            expanded = p.expanduser()
            """Older pythons than 3.8 might still throw an exception"""
            try:
                if expanded.is_file():
                    return expanded
            except:
                continue
        return None

    def get_parser(self):
        return self.parser
