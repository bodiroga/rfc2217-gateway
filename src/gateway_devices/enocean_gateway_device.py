"""Devices from EnOcean GmbH"""

import logging
from gateway_devices.generic_gateway_device import GenericGatewayDevice

logger = logging.getLogger(__name__)


def get_class():
    """Returns the class provided by this module"""
    return EnoceanGatewayDevice


class EnoceanGatewayDevice(GenericGatewayDevice):
    """USB parameters identifying EnOcean devices"""
    NAME = "Enocean"
    ID_MODEL_ID = "6001"
    ID_VENDOR_ID = "0403"
    ID_VENDOR_ENC = "EnOcean\\x20GmbH"
    PORT = 5558
