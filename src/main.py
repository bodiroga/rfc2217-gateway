#!/usr/bin/env python3

import logging
import pyudev
import signal
import time

from device_definitions import devices as registered_devices
from rfc2217_device import RFC2217Device

logging.basicConfig(format='%(asctime)s %(levelname)-8s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)


rfc_devices = {}

def usb_device_event(action, device):
    id_model = device.get("ID_MODEL")
    id_vendor = device.get("ID_VENDOR")
    if not id_model or not id_vendor:
        return
    for rd in registered_devices:
        if id_model == rd.get("ID_MODEL") and id_vendor == rd.get("ID_VENDOR"):
            if action == "add":
                serial_port = device.get("DEVNAME")
                tpc_port = rd.get("PORT")
                logger.info("Device '{}:{}' ('{}') added".format(id_model, id_vendor, serial_port))
                device = RFC2217Device(serial_port, tpc_port)
                device.start()
                rfc_devices[serial_port] = device
            elif action == "remove":
                serial_port = device.get("DEVNAME")
                logger.info("Device '{}:{}' ('{}') removed".format(id_model, id_vendor, serial_port))
                rfc_devices[serial_port].stop()
                del rfc_devices[serial_port]
            break


def signal_handler(signal, frame):
    for device in rfc_devices.values():
        device.stop()
    logger.info("serial2rfc2217 gateway program stopped")


if __name__ == "__main__":
    logger.info("serial2rfc2217 gateway program has started")

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