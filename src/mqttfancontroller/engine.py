# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only


import multiprocessing as mp
from time import sleep

from mqttfancontroller.inputs.timeinput import TimestampInput
from mqttfancontroller.utils.messagebroker import MessageBroker
from mqttfancontroller.outputs.printstdoutput import PrintStdOutput


class Engine:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.stop_event = mp.Event()
        self.broker = MessageBroker(self.stop_event)
        self.needed_procs = [self.broker]
        self.running_procs = []
        self.publish_queue = self.broker.get_publish_queue()
        self.init_needed_procs_from_config()
        self.logger.debug("Engine initialized")

    def start(self):
        """Start the engine"""
        self.logger.info("Starting engine...")
        # Try to start all needed processes
        for target in self.needed_procs:
            process = mp.Process(target=target.start)
            process.start()
            self.running_procs.append(process)

        try:
            while not self.stop_event.is_set():
                sleep(0.1)
                # Check for dead processes and order others to stop if
                # someone has died.
                for process in self.running_procs:
                    if not process.is_alive():
                        self.stop_event.set()

        except KeyboardInterrupt:
            self.logger.debug("Got KeyboardInterrupt")
            self.stop_event.set()
        finally:
            self.logger.info("Stopping engine...")
            for process in self.running_procs:
                process.join()
                process.close()

        self.logger.debug("Engine stopped!")

    def stop(self):
        """Shut down engine gracefully"""
        self.stop_event.set()
        self.logger.debug("Stop event sent")

    def init_needed_procs_from_config(self):
        """Initialize needed processes from config"""
        self.needed_procs.append(
            TimestampInput(
                "UnixTimestampOne",
                self.stop_event,
                self.publish_queue,
                self.broker.get_new_subscriber_queue(),
            )
        )
        self.needed_procs.append(
            PrintStdOutput(
                "PrintStdOne",
                self.stop_event,
                self.publish_queue,
                self.broker.get_new_subscriber_queue(),
            )
        )
