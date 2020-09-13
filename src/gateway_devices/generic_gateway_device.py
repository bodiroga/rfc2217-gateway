#!/usr/bin/env python3

import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class GenericGatewayDevice(object):

    NAME = ""
    ID_MODEL_ID = ""
    ID_VENDOR_ID = ""
    ID_VENDOR_ENC = ""
    PORT = ""

    def __init__(self, device):
        if not self.NAME:
            raise Exception("USB device must provide a 'NAME'")
        if not self.ID_MODEL_ID:
            raise Exception("USB device must provide a 'ID_MODEL_ID'")
        if not self.ID_VENDOR_ID:
            raise Exception("USB device must provide a 'ID_VENDOR_ID'")
        if not self.ID_VENDOR_ENC:
            raise Exception("USB device must provide a 'ID_VENDOR_ENC'")
        if not self.PORT:
            raise Exception("USB device must provide a 'PORT'")
        self.device = device

    @classmethod
    def get_device_identifier(cls):
        if not cls.ID_MODEL_ID or not cls.ID_VENDOR_ID or not cls.ID_VENDOR_ENC:
            raise Exception("Undefined required parameters")
        identifier_string = cls.ID_MODEL_ID + cls.ID_VENDOR_ID + cls.ID_VENDOR_ENC
        return hashlib.sha224(identifier_string.encode('utf-8')).hexdigest()

    def get_name(self):
        return self.NAME

    def get_tcp_port(self):
        return self.PORT

    def get_serial_port(self):
        return self.device.get("DEVNAME")

    def get_id_model(self):
        return self.device.get("ID_MODEL_ID")

    def get_id_vendor(self):
        return self.device.get("ID_VENDOR_ID")
    
    def get_properties(self):
        model_id = self.device.get("ID_MODEL_ID", "")
        model = self.device.get("ID_MODEL", "")
        model_enc = self.device.get("ID_MODEL_ENC", "")
        model_db = self.device.get("ID_MODEL_FROM_DATABASE", "")
        vendor_id = self.device.get("ID_VENDOR_ID", "")
        vendor = self.device.get("ID_VENDOR_FROM_DATABASE", "")
        vendor_enc = self.device.get("ID_VENDOR_ENC", "")
        vendor_db = self.device.get("ID_VENDOR_FROM_DATABASE", "")
        serial = self.device.get("ID_SERIAL", "")
        serial_short = self.device.get("ID_SERIAL_SHORT", "")

        properties = { "MODEL_ID": model_id, "MODEL": model,
                    "MODEL_ENC": model_enc, "MODEL_DB": model_db,
                    "VENDOR_ID": vendor_id, "VENDOR": vendor,
                    "VENDOR_ENC": vendor_enc, "VENDOR_DB": vendor_db,
                    "SERIAL": serial, "SERIAL_SHORT": serial_short }

        return properties
