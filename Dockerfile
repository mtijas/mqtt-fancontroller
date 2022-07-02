# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

FROM python:3.10-slim
  WORKDIR /fancontroller

  RUN useradd -ms /bin/bash fancontroller
  RUN pip install --upgrade pip setuptools wheel

  RUN chown -R fancontroller:fancontroller /fancontroller

  USER fancontroller

  ENV PATH="/home/fancontroller/.local/bin:$PATH"

  ENTRYPOINT ["/bin/bash"]
