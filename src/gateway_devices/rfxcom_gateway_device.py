#!/usr/bin/env python3

import logging
from gateway_devices.generic_gateway_device import GenericGatewayDevice

logger = logging.getLogger(__name__)


def get_class():
    return RFXComGatewayDevice


class RFXComGatewayDevice(GenericGatewayDevice):

    NAME = "RFXCOM RFXtrx433"
    ID_MODEL_ID = "6001"
    ID_VENDOR_ID = "0403"
    ID_VENDOR_ENC = "RFXCOM"
    PORT = 5557
