# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only


import multiprocessing as mp
from time import sleep

from mqttfancontroller.modules.printstdoutput import PrintStdOutput
from mqttfancontroller.modules.timeinput import TimestampInput
from mqttfancontroller.utils.messagebroker import MessageBroker
from mqttfancontroller.modules.mqtt import MQTTMessenger


class Engine:
    available_modules = {
        "timestamp": TimestampInput,
        "stdout": PrintStdOutput,
        "mqtt": MQTTMessenger,
    }

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.stop_event = mp.Event()
        self.broker = MessageBroker(self.stop_event)
        self.needed_procs = [self.broker]
        self.running_procs = []
        self.logger.debug("Engine initialized")

    def start(self):
        """Start the engine"""
        self.logger.info("Starting engine...")
        self.init_needed_procs_from_config()
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
        modules = self.config["modules"].get(list)

        for module in modules:
            module_type = module["type"]
            module_config = dict()
            if module_type not in self.available_modules:
                raise AttributeError(f"Module '{module}' is not installed.")

            (pub_q, sub_q) = self.broker.get_client_queues()
            if "config" in module:
                module_config = module["config"]

            if "env" in self.config:
                if module_type in self.config["env"]:
                    for k, v in self.config["env"][module_type].items():
                        module_config[k] = str(v)

            module_instance = self.available_modules[module_type](
                config=module_config,
                stop_event=self.stop_event,
                pub_queue=pub_q,
                sub_queue=sub_q,
            )
            self.needed_procs.append(module_instance)
