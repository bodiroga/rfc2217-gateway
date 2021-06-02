"""SARAD instruments with integrated FT232 USB serial converter"""

import logging
from typing import Type

from sarad.cluster import SaradCluster

from gateway_devices.generic_gateway_device import GenericGatewayDevice

logger = logging.getLogger(__name__)


def get_class() -> Type[GenericGatewayDevice]:
    """Returns the class provided by this module"""
    return SaradGatewayDevice


class SaradGatewayDevice(GenericGatewayDevice):
    """SARAD instrument with RTM-1688 protocol"""

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
            self.__devi = self.__cluster.update_connected_instruments(
                [device.get("DEVNAME")]
            )
        except Exception:  # pylint: disable = broad-except
            logger.error("USB Device Access Failed %s", device)
        self.get_properties()

    def get_serial_id(self):
        if len(self.__devi) == 1:
            return f"{self.device.get('ID_MODEL', '')}:{self.__devi[0].device_id}"
        return self.device.get("ID_SERIAL", "")

    def get_properties(self):
        if len(self.__devi) == 1:
            model = self.device.get("ID_MODEL", "")
            serial_short = f"{self.__devi[0].device_id}.{self.get_protocol()}"
            self.serial = serial_short
            return {
                "MODEL_ID": self.device.get("ID_MODEL_ID", ""),
                "MODEL": model,
                "MODEL_ENC": self.device.get("ID_MODEL_ENC", ""),
                "MODEL_DB": self.device.get("ID_MODEL_FROM_DATABASE", ""),
                "VENDOR_ID": self.device.get("ID_VENDOR_ID", ""),
                "VENDOR": self.device.get("ID_VENDOR_FROM_DATABASE", ""),
                "VENDOR_ENC": self.device.get("ID_VENDOR_ENC", ""),
                "VENDOR_DB": self.device.get("ID_VENDOR_FROM_DATABASE", ""),
                "SERIAL": f"{model}_{serial_short}",
                "SERIAL_SHORT": f"{self.__devi[0].device_id}.{self.get_protocol()}",
            }
        return super().get_properties()

    def get_name_unique(self):
        return f"{self.serial}"
