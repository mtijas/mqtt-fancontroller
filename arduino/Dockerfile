# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only

FROM debian:bullseye-slim
    ENV ARDUINO_PLATFORM "arduino:avr"

    WORKDIR /arduino

    RUN mkdir /arduino/.arduino15
    COPY ./arduino-cli.yaml /arduino/.arduino15/arduino-cli.yaml

    RUN apt update
    RUN apt install -y curl

    RUN curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=/usr/local/bin sh

    COPY ./upload-sketch.sh .
    RUN chmod +x upload-sketch.sh

    RUN arduino-cli core install $ARDUINO_PLATFORM

    ENTRYPOINT ["./upload-sketch.sh"]
