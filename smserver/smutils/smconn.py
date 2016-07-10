#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime
import logging
from threading import Lock
from smserver.smutils import smpacket

class StepmaniaConn(object):
    logger = logging.getLogger('stepmania')
    ENCODING = "binary"
    ALLOWED_PACKET = []

    def __init__(self, serv, ip, port):
        self.mutex = Lock()
        self.ip = ip
        self.port = port
        self.users = []
        self.room = None
        self.logged_users = []
        self.songs = {}
        self.song = None
        self.songstats = {0: {"data": []}, 1: {"data": []}}
        self.wait_start = False
        self.ingame = False

        self.last_ping = datetime.datetime.now()
        self.stepmania_version = None
        self.stepmania_name = None
        self._serv = serv

    def run(self):
        for data in self.received_data():
            if data is None:
                break

            self._on_data(data)

        self.close()

    def received_data(self):
        pass

    def _on_data(self, data):
        packet = smpacket.SMPacket.from_(self.ENCODING, data)
        if not packet:
            self.logger.info("packet %s drop from %s" % (data, self.ip))
            return None

        self.logger.debug("Packet received from %s: %s" % (self.ip, packet))

        if self.ALLOWED_PACKET and packet.command not in self.ALLOWED_PACKET:
            self.logger.debug("packet %s ignored from %s" % (data, self.ip))
            return None

        if packet.command == smpacket.SMClientCommand.NSCPingR:
            self.last_ping = datetime.datetime.now()

        self._serv.on_packet(self, packet)

    def send(self, packet):
        self.logger.debug("packet send to %s: %s" % (self.ip, packet))
        self._send_data(packet.to_(self.ENCODING))

    def _send_data(self, data):
        pass

    def close(self):
        self._serv.on_disconnect(self)

