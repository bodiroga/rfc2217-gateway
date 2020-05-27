#!/usr/bin/env python3

import logging
import pyudev
import signal

logging.basicConfig(format='%(asctime)s %(levelname)-8s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

def usb_device_event(action, device):
    id_model = device.get("ID_MODEL")
    id_vendor = device.get("ID_VENDOR")
    if not id_model or not id_vendor:
        return
    if action == "add":
        logger.info("Device '{}:{}' added".format(id_model, id_vendor))
    elif action == "remove":
        logger.info("Device '{}:{}' removed".format(id_model, id_vendor))

def signal_handler(signal, frame):
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