#!/usr/bin/env python3

import logging
import pyudev
import signal
import time

from device_definitions import devices as registered_devices
from mdns_advertiser import MDNSAdvertiser
from rfc2217_device import RFC2217Device

logging.basicConfig(format='%(asctime)s %(levelname)-8s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

INTERFACE = "wlp2s0"

rfc_devices = {}
rfc_advertisers = {}

def properties_from_device(device):
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


def search_in_registered_devices(device, registered_devices):
    for rd in registered_devices:
        match = True
        for id, value in rd["ID"].items():
            if device.get(id) != value:
                match = False
                break
        if match:
            return rd


def usb_device_event(action, device):
    id_model = device.get("ID_MODEL_ID")
    id_vendor = device.get("ID_VENDOR_ID")
    serial_port = device.get("DEVNAME")
    if not id_model or not id_vendor:
        return
    rd = search_in_registered_devices(device, registered_devices)
    if not rd:
        return
    if action == "add":
        tpc_port = rd.get("PORT")
        logger.info("Device '{}:{}' ('{}') added".format(id_model, id_vendor, serial_port))
        properties = properties_from_device(device)
        advertiser = MDNSAdvertiser("_rfc2217", "RFC2217 ({}:{})".format(id_vendor, id_model),
                                rd.get("PORT"), properties, None, INTERFACE)
        device = RFC2217Device(serial_port, tpc_port)
        device.start()
        advertiser.start()
        rfc_devices[serial_port] = device
        rfc_advertisers[serial_port] = advertiser
    elif action == "remove":
        logger.info("Device '{}:{}' ('{}') removed".format(id_model, id_vendor, serial_port))
        rfc_devices[serial_port].stop()
        rfc_advertisers[serial_port].stop()
        del rfc_devices[serial_port]
        del rfc_advertisers[serial_port]


def signal_handler(signal, frame):
    for device in rfc_devices.values():
        device.stop()
    for advertiser in rfc_advertisers.values():
        advertiser.stop()
    logger.info("RFC2217 Gateway stopped")


if __name__ == "__main__":
    logger.info("RFC2217 Gateway started")

    context = pyudev.Context()
    for device in context.list_devices(subsystem='tty'):
        usb_device_event("add", device)

    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('tty')

    usb_stick_observer = pyudev.MonitorObserver(monitor, usb_device_event)
    usb_stick_observer.start()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.pause()