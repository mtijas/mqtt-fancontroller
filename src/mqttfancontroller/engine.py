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
        (pub_q, sub_q) = self.broker.get_client_queues()
        self.needed_procs.append(
            TimestampInput(
                config={"name": "UnixTimestampOne", "update_interval": 2},
                stop_event=self.stop_event,
                pub_queue=pub_q,
                sub_queue=sub_q,
            )
        )
        (pub_q, sub_q) = self.broker.get_client_queues()
        self.needed_procs.append(
            PrintStdOutput(
                config={"name": "PrintStdOne"},
                stop_event=self.stop_event,
                pub_queue=pub_q,
                sub_queue=sub_q,
            )
        )
        (pub_q, sub_q) = self.broker.get_client_queues()
        ts2 = TimestampInput(
            config={"name": "UnixTimestampTwo", "update_interval": 5},
            stop_event=self.stop_event,
            pub_queue=pub_q,
            sub_queue=sub_q,
        )
        self.needed_procs.append(ts2)
