#!/usr/bin/env python3

import logging
from gateway_devices.generic_gateway_device import GenericGatewayDevice
from sarad.cluster import SaradCluster

logger = logging.getLogger(__name__)

def get_class():
    return FTDIGatewayDevice

class FTDIGatewayDevice(GenericGatewayDevice):

    NAME = "FT232R USB UART"
    ID_MODEL_ID = "6001"
    ID_VENDOR_ID = "0403"
    ID_VENDOR_ENC = "FTDI"

    PORT_RANGE = [5600, 5640]
    PROTOCOL = "unknown"

    def __init__(self, device):
        super().__init__(device)
        self.__cluster = SaradCluster([self.get_serial_port()])
        try:
            self.__devi = self.__cluster.update_connected_instruments()
        except Exception:
            logger.error(f"USB Device Access Failed {device}")
            pass
        self.get_properties()


    def get_serial_id(self):

        if len(self.__devi)==1 :
            return "{}:{}".format(self.device.get("ID_MODEL", ""), self.__devi[0].get_id())
        else:
            return self.device.get("ID_SERIAL", "")

    def get_properties(self):
        if len(self.__devi)>=1 :
            self.model_id = self.device.get("ID_MODEL_ID", "")
            self.model = self.device.get("ID_MODEL", "")
            self.model_enc = self.device.get("ID_MODEL_ENC", "")
            self.model_db = self.device.get("ID_MODEL_FROM_DATABASE", "")
            self.vendor_id = self.device.get("ID_VENDOR_ID", "")
            self.vendor = self.device.get("ID_VENDOR_FROM_DATABASE", "")
            self.vendor_enc = self.device.get("ID_VENDOR_ENC", "")
            self.vendor_db = self.device.get("ID_VENDOR_FROM_DATABASE", "")
            self.serial_short = str(self.__devi[0].device_id)
            self.serial = f'{self.serial_short}'

            properties = { "MODEL_ID": self.model_id, "MODEL": self.model,
                    "MODEL_ENC": self.model_enc, "MODEL_DB": self.model_db,
                    "VENDOR_ID": self.vendor_id, "VENDOR": self.vendor,
                    "VENDOR_ENC": self.vendor_enc, "VENDOR_DB": self.vendor_db,
                    "SERIAL": "{}_{}".format(self.model,self.serial_short), "SERIAL_SHORT": self.serial_short
                    }
            return properties
        else:
            return super().get_properties()

    def get_name_unique(self):
        return f'{self.serial}'
