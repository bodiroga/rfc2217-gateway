#!/usr/bin/env python3

import logging
from gateway_devices.generic_gateway_device import GenericGatewayDevice
from SarI import SaradCluster

logger = logging.getLogger(__name__)

def get_class():
    return SaradGatewayDevice

class SaradGatewayDevice(GenericGatewayDevice):

    NAME = "SARAD"
    ID_MODEL_ID = "6001"
    ID_VENDOR_ID = "0403"
    ID_VENDOR_ENC = "SARAD"
    PORT_RANGE = [5560, 5580]
    PROTOCOL = "sarad-1688"
    
    def __init__(self, device):
        super().__init__(device)
        self.__cluster = SaradCluster()
        try:
            self.__devi = self.__cluster.update_connected_instruments([self.get_serial_port()])
        except Exception:
            logger.error("USB Device Access Failed")
            pass
    
        
    def get_serial_id(self):
        
        if len(self.__devi)==1 :
            return "{}:{}".format(self.device.get("ID_MODEL", ""), self.__devi[0].get_id())
        else:
            return self.device.get("ID_SERIAL", "")
        
    def get_properties(self):
        if len(self.__devi)==1 :
            model_id = self.device.get("ID_MODEL_ID", "")
            model = self.device.get("ID_MODEL", "")
            model_enc = self.device.get("ID_MODEL_ENC", "")
            model_db = self.device.get("ID_MODEL_FROM_DATABASE", "")
            vendor_id = self.device.get("ID_VENDOR_ID", "")
            vendor = self.device.get("ID_VENDOR_FROM_DATABASE", "")
            self.vendor_enc = self.device.get("ID_VENDOR_ENC", "")
            vendor_db = self.device.get("ID_VENDOR_FROM_DATABASE", "")
            serial_short = str(self.__devi[0].get_id())
            self.serial = f'{vendor_enc}_{serial_short}'

            properties = { "MODEL_ID": model_id, "MODEL": model,
                    "MODEL_ENC": model_enc, "MODEL_DB": model_db,
                    "VENDOR_ID": vendor_id, "VENDOR": vendor,
                    "VENDOR_ENC": vendor_enc, "VENDOR_DB": vendor_db,
                    "SERIAL": "{}_{}".format(model,serial_short), "SERIAL_SHORT": serial_short
                    }
            return properties
        else:
            return super().get_properties()
        
    def get_name_unique(self):    
        return f'{self.vendor_enc}_{self.serial}'

