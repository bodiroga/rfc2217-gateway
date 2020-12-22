#!/usr/bin/env python

import logging
import socket
import time
import threading
import netifaces as ni

from zeroconf import ServiceInfo, Zeroconf

logger = logging.getLogger(__name__)


class MDNSAdvertiser(object):
    def __init__(self, type_, name, port, properties, server, interface):
        self.type = type_
        self.name = name
        self.interface = interface if interface else "eth0"
        self.address = self.get_network_ip_address(interface)
        self.port = port
        self.properties = properties
        self.server = server if server else socket.gethostname()
        self.service = None
        self.advertiser_thread = None
        self.connectivity_thread = None
        self.alive = None

    @staticmethod
    def get_network_ip_address(interface='eth0'):
        """
        Get the first IP address of a network interface.
        :param interface: The name of the interface.
        :return: The IP address.
        """

        if interface not in ni.interfaces():
            logger.error('Could not find interface {}.'.format(interface))
            return None
        interface = ni.ifaddresses(interface)
        if (2 not in interface) or (len(interface[2]) == 0):
            logger.warning(
                'Could not find IP of interface {}.'.format(interface))
            return None
        return interface[2][0]['addr']

    def start(self):
        self.alive = True
        self.connectivity_thread = threading.Thread(
            target=self.__check_connectivity)
        self.connectivity_thread.setDaemon(1)
        self.connectivity_thread.start()

    def stop(self):
        if self.alive:
            self.alive = False
            if self.connectivity_thread:
                self.connectivity_thread.join()
            if self.advertiser_thread:
                self.advertiser_thread.join()
        logger.debug("mDNS advertiser stopped")

    def __check_connectivity(self):
        while self.alive and not self.address:
            self.address = self.get_network_ip_address(self.interface)
            time.sleep(1)

        if self.alive:
            self.advertiser_thread = threading.Thread(
                target=self.__start_advertising)
            self.advertiser_thread.setDaemon(1)
            self.advertiser_thread.start()
            logger.debug("mDNS advertiser started")

    def __start_advertising(self):
        self.service = ServiceInfo("{}._tcp.local.".format(self.type),
                                   "{}.{}._tcp.local.".format(
                                       self.name, self.type),
                                   port=self.port,
                                   weight=0,
                                   priority=0,
                                   properties=self.properties,
                                   server="{}.local.".format(self.server),
                                   addresses=[socket.inet_aton(self.address)])

        zeroconf = Zeroconf()
        zeroconf.register_service(self.service)

        while self.alive:
            time.sleep(.5)

        zeroconf.unregister_service(self.service)
        zeroconf.close()
