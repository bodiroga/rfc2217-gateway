#!/usr/bin/env python3

import logging
import importlib
import os

logger = logging.getLogger("gateway_devices")

folder = os.path.dirname(os.path.abspath(__file__))

EXCLUDED_FILE_NAMES = ["__init__.py", "generic_gateway_device.py"]

__all__ = {}

for file_name in os.listdir(folder):
    file_path = "/".join((folder, file_name))
    if os.path.isfile(file_path):
        if file_name in EXCLUDED_FILE_NAMES:
            continue
        file_base = file_name.replace('.py', '')
        module_path = "{}.{}".format(__name__, file_base)
        try:
            module = importlib.import_module(module_path)
        except Exception as e:
            logger.error("Error loading device definition at {}: \n{}".format(module_path, e))
        else:
            module_class = module.get_class()
            module_device_identifier = module_class.get_device_identifier()
            __all__[module_device_identifier] = module_class