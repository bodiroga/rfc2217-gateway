#!/usr/bin/env python3

import logging
import pyudev
import signal
import time

from usb_devices_handler import UsbDevicesHandler

logging.basicConfig(format='%(asctime)s %(levelname)-6s - %(name)-16s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

INTERFACE = "wlp2s0"


def usb_device_event(action, device):
    if not devices_handler.is_valid_device(device):
        return

    logger.debug("Device at '{}' is a valid device".format(device.get("DEVNAME")))
    if action == "add":
        devices_handler.create_usb_device(device)
    elif action == "remove":
        devices_handler.delete_usb_device(device)


def signal_handler(signal, frame):
    devices_handler.stop_all_devices()
    logger.info("RFC2217 Gateway stopped")


if __name__ == "__main__":
    logger.info("RFC2217 Gateway started")

    devices_handler = UsbDevicesHandler(INTERFACE)

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