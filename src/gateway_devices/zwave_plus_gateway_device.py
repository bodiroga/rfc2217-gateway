#!/usr/bin/env python3

import logging
import time
import threading
from typing import Type
import serial
from gateway_devices.generic_gateway_device import GenericGatewayDevice

logger = logging.getLogger(__name__)


def get_class() -> Type[GenericGatewayDevice]:
    return ZWavePlusGatewayDevice


class ZWavePlusGatewayDevice(GenericGatewayDevice):

    NAME = "Aeotec ZStick Gen5"
    ID_MODEL_ID = "0200"
    ID_VENDOR_ID = "0658"
    ID_VENDOR_ENC = "0658"
    PORT = 5555

    def __init__(self, device):
        super().__init__(device)
        self.serial_port = self.device.get("DEVNAME")
        self.home_id_handler = ZWaveHomeIdHandler(self.serial_port)
        self.home_id_handler.start()

    def get_properties(self):
        properties = super().get_properties()
        home_id = self.home_id_handler.get_home_id()
        properties["HOME_ID"] = home_id
        return properties


class ZWaveHomeIdHandler():

    NAK = b'\x15'
    MEMORY_ID_COMMAND = b'\x01\x03\x00\x20\xdc'

    def __init__(self, serial_port):
        self.home_id = None
        self.serial_port = serial_port
        self.zwave_connection = serial.Serial(self.serial_port,
                                              baudrate=115200,
                                              timeout=0.1)
        self.zwave_receiver = ZWaveHomeIdReceiver(self.zwave_connection,
                                                  self.__on_home_id_received)
        self.zwave_receiver.start()

    def start(self):
        self.zwave_connection.write(self.NAK)
        self.zwave_connection.write(self.MEMORY_ID_COMMAND)

    def stop(self):
        self.zwave_receiver.stop()
        self.zwave_connection.close()

    def get_home_id(self):
        while not self.home_id:
            time.sleep(0.1)
        return self.home_id

    def __on_home_id_received(self, home_id):
        self.home_id = home_id
        self.stop()


class ZWaveHomeIdReceiver():

    SEARCH_SOF = 0
    SEARCH_LEN = 1
    SEARCH_DAT = 2

    SOF = b'\x01'
    ACK = b'\x06'
    NAK = b'\x15'
    CAN = b'\x18'

    TIMEOUT = b''

    def __init__(self, serial_connection, on_home_id_received):
        self.zwave_connection = serial_connection
        self.on_home_id_received = on_home_id_received
        self.rx_buffer = []
        self.rx_state = self.SEARCH_SOF
        self.rx_length = 0
        self.message_length = 0
        self.zwave_reader_thread = None
        self.reading = False

    def start(self):
        logger.debug("Starting ZWave Receiver")
        self.reading = True
        self.zwave_reader_thread = threading.Thread(target=self.__zwave_reader)
        self.zwave_reader_thread.start()

    def stop(self):
        logger.debug("Stopping ZWave Receiver")
        self.reading = False

    def __zwave_reader(self):
        logger.debug("ZWave Reader thread started")
        while self.reading:
            try:
                next_byte = self.zwave_connection.read(1)
            except TypeError:
                logger.debug("Serial connection error")
                break

            if next_byte == self.TIMEOUT:
                continue

            if self.rx_state == self.SEARCH_SOF:
                if next_byte == self.SOF:
                    logger.debug("SOF detected, fine")
                    self.rx_state = self.SEARCH_LEN
                elif next_byte == self.ACK:
                    logger.debug("ACK detected, fine")
                elif next_byte in [self.NAK, self.CAN]:
                    logger.error("Unexpected command")
                else:
                    logger.error("Unkown '%s'", next_byte)
            elif self.rx_state == self.SEARCH_LEN:
                self.message_length = int.from_bytes(next_byte, "big")
                self.rx_state = self.SEARCH_DAT
            elif self.rx_state == self.SEARCH_DAT:
                self.rx_buffer.append(int.from_bytes(next_byte, "big"))
                self.rx_length += 1

                if self.rx_length < self.message_length:
                    continue

                home_id = self.__get_home_id(self.rx_buffer)
                if home_id != -1:
                    self.rx_buffer = []
                    self.rx_state = self.SEARCH_SOF
                    self.rx_length = 0
                    self.message_length = 0
                    self.zwave_connection.write(self.ACK)
                    threading.Thread(target=self.on_home_id_received,
                                     args=[home_id]).start()
                else:
                    logger.error("Incorrect Home ID received!")

        logger.debug("ZWave Reader thread stopped")

    def __get_home_id(self, message):
        if message[0] != 1:  # Check if the message is a response message (1)
            return -1
        if message[
                1] != 32:  # Check if the message is a response to a 0x20 message
            return -1
        if message[-2] != 1:  # Check if node id is 1
            return -1

        home_id = ""
        for i in range(2, 6, 1):
            hex_value = hex(message[i])
            home_id += hex_value[-2:]

        logger.debug("Home ID: %s", home_id)
        return home_id
