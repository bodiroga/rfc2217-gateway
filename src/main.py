#!/usr/bin/env python3

import logging
import pyudev
import signal
import time

from device_definitions import devices as registered_devices
from mdns_advertiser import MDNSAdvertiser
from rfc2217_device import RFC2217Device
from usb_device_helper import UsbDeviceHelper

logging.basicConfig(format='%(asctime)s %(levelname)-6s - %(name)-16s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

INTERFACE = "wlp2s0"

rfc_devices = {}
rfc_advertisers = {}

def usb_device_event(action, device):
    id_model = device.get("ID_MODEL_ID")
    id_vendor = device.get("ID_VENDOR_ID")
    serial_port = device.get("DEVNAME")
    if not id_model or not id_vendor:
        return
    rd = usb_helper.search_in_registered_devices(device)
    if not rd:
        return
    if action == "add":
        tpc_port = rd.get("PORT")
        logger.info("Device '{}:{}' ('{}') added".format(id_model, id_vendor, serial_port))
        properties = usb_helper.properties_from_device(device)
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

    usb_helper = UsbDeviceHelper(registered_devices)

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