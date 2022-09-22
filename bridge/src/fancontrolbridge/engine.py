# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-License-Identifier: GPL-3.0-only


import multiprocessing as mp
from importlib import import_module
from time import sleep

from fancontrolbridge.utils.messagebroker import MessageBroker


class Engine:
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
        raw_modules_list = self.config["modules"].get(list)
        self.logger.debug(f"Got modules config: {raw_modules_list}")
        for module in raw_modules_list:
            actual_module = self._load_external_module(module["type"])
            if not actual_module:
                self.stop_event.set()
                break
            module_config = self._get_module_config(module)
            (pub_q, sub_q) = self.broker.get_client_queues()
            module_instance = actual_module.main(
                config=module_config,
                stop_event=self.stop_event,
                pub_queue=pub_q,
                sub_queue=sub_q,
            )
            self.needed_procs.append(module_instance)

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

    def _load_external_module(self, name):
        """Import module from modules directory"""
        full_name = f"fancontrolbridge.modules.{name.lower()}.main"
        try:
            imported_module = import_module(full_name)
        except ImportError:
            self.logger.critical(f"Module {full_name} could not be loaded.")
            return None
        return imported_module

    def _get_module_config(self, module) -> dict:
        """Extracts module config from raw list item and augments it
        with env variables"""
        module_config = dict()
        if "config" in module:
            module_config = module["config"]

        if module["type"] in self.config:
            for k, v in self.config[module["type"]].items():
                module_config[k] = str(v)
                self.logger.debug(f"Imported config {k} with content {str(v)}")

        return module_config
