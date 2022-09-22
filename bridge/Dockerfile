# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

FROM python:3.10-slim
    WORKDIR /bridge

    RUN useradd -ms /bin/bash bridge
    RUN usermod -aG dialout bridge
    RUN pip install --upgrade pip setuptools wheel

    RUN chown -R bridge:bridge /bridge

    USER bridge

    ENV PATH="/home/bridge/.local/bin:$PATH"

    ENTRYPOINT ["/bin/bash"]
