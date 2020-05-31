#!/usr/bin/env python

import logging
import serial
import socket
import threading
import time

from rfc2217_redirector import Redirector

logger = logging.getLogger(__name__)

class RFC2217Device(object):
    def __init__(self, device_path, tcp_port):
        self.device_path = device_path
        self.tcp_port = tcp_port
        self.s_port = self.connect_serial_port(self.device_path)
        self.s_socket = self.create_socket(self.tcp_port)
        self.s_redirector = None
        self.started = False

    def connect_serial_port(self, port_path):
        ser = serial.serial_for_url(port_path, do_not_open=True)
        ser.timeout = 3
        ser.dtr = False
        ser.rts = False
        ser.open()

        return ser

    def create_socket(self, port):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(('', port))
        srv.listen(1)
        srv.setblocking(0)

        return srv

    def start(self):
        self.started = True
        self.thread = threading.Thread(target=self.__start)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.started = False
        if self.s_redirector:
            self.s_redirector.stop()
        self.thread.join()
        self.s_port.close()
        self.s_socket.shutdown(socket.SHUT_RDWR)
        self.s_socket.close()
        logger.debug("RFCDevice '{}' completely stopped".format(self.device_path))

    def __start(self):
        logger.debug("RFCDevice ('{}') main loop started".format(self.device_path))
        while(self.started):
            try:
                client_socket, addr = self.s_socket.accept()
            except BlockingIOError:
                time.sleep(0.5)
                continue
            logging.debug('Connected by {}:{}'.format(addr[0], addr[1]))
            client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.s_port.dtr = True
            self.s_port.rts = True
            self.s_redirector = Redirector(self.s_port, client_socket)
            try:
                self.s_redirector.shortcircuit()
            finally:
                self.s_redirector.stop()
                client_socket.shutdown(socket.SHUT_RDWR)
                client_socket.close()
                try:
                    self.s_port.rts = False
                    self.s_port.dtr = False
                except:
                    pass
        logger.debug("RFCDevice ('{}') main loop stopped".format(self.device_path))