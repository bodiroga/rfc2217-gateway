#!/usr/bin/env python
#
# redirect data from a TCP/IP connection to a serial port and vice versa
# using RFC 2217
#
# (C) 2009-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import logging
import socket
import threading
import time

import serial.rfc2217


class Redirector:
    def __init__(self, serial_instance, socket, debug=False):
        self.serial = serial_instance
        self.socket = socket
        self.socket.settimeout(1.0)
        self._write_lock = threading.Lock()
        self.rfc2217 = serial.rfc2217.PortManager(
            self.serial,
            self,
            logger=logging.getLogger("rfc2217.server") if debug else None,
        )
        self.log = logging.getLogger("redirector")

    def statusline_poller(self):
        self.log.debug("Status line poll thread started")
        while self.alive:
            time.sleep(0.5)
            try:
                self.rfc2217.check_modem_lines()
            except OSError:
                break
        self.log.debug("Status line poll thread terminated")

    def shortcircuit(self):
        """connect the serial port to the TCP port by copying everything
        from one side to the other"""
        self.alive = True
        self.thread_read = threading.Thread(target=self.reader)
        self.thread_read.daemon = True
        self.thread_read.name = "serial->socket"
        self.thread_read.start()
        self.thread_poll = threading.Thread(target=self.statusline_poller)
        self.thread_poll.daemon = True
        self.thread_poll.name = "status line poll"
        self.thread_poll.start()
        self.writer()

    def reader(self):
        """loop forever and copy serial->socket"""
        self.log.info("Reader started")
        while self.alive:
            try:
                data = self.serial.read(self.serial.in_waiting or 1)
                if data:
                    # escape outgoing data when needed
                    # (Telnet IAC (0xff) character)
                    self.log.info("--> %s", list(self.rfc2217.escape(data)))
                    self.write(b"".join(self.rfc2217.escape(data)))
            except socket.error as msg:
                self.log.error("%s", msg)
                # probably got disconnected
                break
        self.alive = False
        self.log.debug("Reader thread terminated")

    def write(self, data):
        """thread safe socket write with no data escaping.
        Used to send telnet stuff"""
        retries = 3
        with self._write_lock:
            while retries:
                try:
                    self.socket.sendall(data)
                    retries = 0
                except:
                    self.log.debug("retry --> %s", data)
                    retries -= 1

    def writer(self):
        """loop forever and copy socket->serial"""
        while self.alive:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                self.log.info("<-- %s", list(self.rfc2217.filter(data)))
                self.serial.write(b"".join(self.rfc2217.filter(data)))
                self.log.debug("serial.write")
                self.log.debug("%s", b"".join(self.rfc2217.filter(data)))
            except socket.timeout:
                self.log.debug("socket timeout")
                pass
            except socket.error as msg:
                self.log.error("Writer error: %s", msg)
                # probably got disconnected
                break
        self.stop()

    def stop(self):
        """Stop copying"""
        self.log.debug("stopping")
        if self.alive:
            self.alive = False
            self.thread_read.join()
            self.thread_poll.join()
