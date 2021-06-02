"""Define namespace package gateway_devices.

Every module defines a class of devices that will be published.
device_classes is a variable in the namespace of this package
providing a dictionary of module classes."""

import logging
import importlib
import os
from typing import Dict, Any

logger = logging.getLogger("gateway_devices")

folder = os.path.dirname(os.path.abspath(__file__))

EXCLUDED_FILE_NAMES = ["__init__.py", "generic_gateway_device.py"]

device_classes: Dict[str, Any] = {}

for file_name in os.listdir(folder):
    FILE_PATH = "/".join((folder, file_name))
    if os.path.isfile(FILE_PATH):
        if file_name in EXCLUDED_FILE_NAMES:
            continue
        file_base = file_name.replace('.py', '')
        MODULE_PATH = "{}.{}".format(__name__, file_base)
        try:
            module = importlib.import_module(MODULE_PATH)
        except Exception as broad_except:  # pylint: disable=broad-except
            logger.error("Error loading device definition at %s: \n%s",
                         MODULE_PATH, broad_except)
        else:
            module_class = module.get_class()  # type: ignore
            module_device_identifier = module_class.get_device_identifier()
            device_classes[module_device_identifier] = module_class
