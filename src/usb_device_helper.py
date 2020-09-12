#!/usr/bin/env python

import logging

logger = logging.getLogger(__name__)

class UsbDeviceHelper(object):
    def __init__(self, registered_devices):
        self.registered_devices = registered_devices

    def search_in_registered_devices(self, device):
        for rd in self.registered_devices:
            match = True
            for id, value in rd["ID"].items():
                if device.get(id) != value:
                    match = False
                    break
            if match:
                return rd

    def properties_from_device(self, device):
        model_id = device.get("ID_MODEL_ID", "")
        model = device.get("ID_MODEL", "")
        model_enc = device.get("ID_MODEL_ENC", "")
        model_db = device.get("ID_MODEL_FROM_DATABASE", "")
        vendor_id = device.get("ID_VENDOR_ID", "")
        vendor = device.get("ID_VENDOR_FROM_DATABASE", "")
        vendor_enc = device.get("ID_VENDOR_ENC", "")
        vendor_db = device.get("ID_VENDOR_FROM_DATABASE", "")
        serial = device.get("ID_SERIAL", "")
        serial_short = device.get("ID_SERIAL_SHORT", "")

        properties = { "MODEL_ID": model_id, "MODEL": model,
                    "MODEL_ENC": model_enc, "MODEL_DB": model_db,
                    "VENDOR_ID": vendor_id, "VENDOR": vendor,
                    "VENDOR_ENC": vendor_enc, "VENDOR_DB": vendor_db,
                    "SERIAL": serial, "SERIAL_SHORT": serial_short }

        return properties