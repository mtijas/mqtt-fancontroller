# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

from dataclasses import dataclass


@dataclass
class Message:
    event: str
    data: dict
