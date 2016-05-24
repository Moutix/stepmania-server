#!/usr/bin/env python3
# -*- coding: utf8 -*-

import socket
import datetime
import logging
import time
from threading import Thread, Lock

from smutils import smpacket

class StepmaniaThread(Thread):
    _FPS = 60
    logger = logging.getLogger('stepmania')

    def __init__(self, serv, conn, ip, port):
        Thread.__init__(self)
        self.mutex = Lock()
        self.ip = ip
        self.port = port
        self.users = {}
        self.last_ping = datetime.datetime.now()
        self.stepmania_version = None
        self.stepmania_name = None
        self._serv = serv
        self._conn = conn

        self.logger.info("New connection: %s on port %s" % (ip, port))

    @property
    def active_users(self):
        return [user.get("id") for user in self.users.values() if user.get("#")]

    @property
    def online_users(self):
        return [user["id"] for user in self.users.values() if user.get("id")]

    def user_by_pos(self, pos):
        users = [user["id"] for user in self.users.values() if user.get("pos") == pos]
        if not users:
            return None

        return users[0]

    def run(self):
        while True:
            try:
                data = self.received_data()
            except socket.error:
                self._serv.on_disconnect(self)
                break

            self._on_data(data)

        with self._serv.mutex:
            self._serv.connections.remove(self)
        self._conn.close()

    def send_ping(self):
        while True:
            self.send(smpacket.SMPacketServerNSCPing())
            time.sleep(self._FPS)

    def received_data(self):
        full_data = b""
        size = None
        while size is None or len(full_data) - 4 < size:
            data = self._conn.recv(8192)
            if data == b'':
                raise socket.error

            full_data += data
            if not size and len(full_data) > 4:
                size = int.from_bytes(full_data[:4], byteorder='big')

        return full_data

    def _on_data(self, data):
        packet = smpacket.SMPacket.parse_binary(data)
        if not packet:
            self.logger.info("packet %s drop from %s" % (data, self.ip))
            return None

        self.logger.debug("Packet received from %s: %s" % (self.ip, packet))

        self._serv.on_packet(self, packet)

    def send(self, packet):
        with self.mutex:
            self.logger.debug("packet send to %s: %s" % (self.ip, packet))
            self._conn.sendall(packet.binary)

class StepmaniaServer(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.mutex = Lock()
        self.connections = []
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.ip, self.port))
        self._socket.listen(5)

    def start(self):
        while 1:
            conn, addr = self._socket.accept()
            thread = StepmaniaThread(self, conn, *addr)
            with self.mutex:
                self.connections.append(thread)
            thread.start()

    def sendall(self, packet):
        for conn in self.connections:
            conn.send(packet)

    def on_packet(self, serv, packet):
        func = getattr(self, "on_%s" % packet.command.name.lower(), None)
        if not func:
            return None

        func(serv, packet)

    def on_disconnect(self, serv):
        pass

    def on_nscping(self, serv, packet):
        serv.send(smpacket.SMPacketServerNSCPingR())

    def on_nscpingr(self, serv, packet):
        with serv.mutex:
            serv.last_ping = datetime.datetime.now()

    def on_nschello(self, serv, packet):
        serv.send(smpacket.SMPacketServerNSCHello(version=128, name="Stepmania-Server"))

    def on_nscgsr(self, serv, packet):
        pass

    def on_nscgon(self, serv, packet):
        pass

    def on_nscgsu(self, serv, packet):
        pass

    def on_nscsu(self, serv, packet):
        pass

    def on_nsccm(self, serv, packet):
        pass

    def on_nscrsg(self, serv, packet):
        pass

    def on_nsccuul(self, serv, packet):
        pass

    def on_nsscsms(self, serv, packet):
        pass

    def on_nscuopts(self, serv, packet):
        pass

    def on_nssmonl(self, serv, packet):
        func = getattr(self, "on_%s" % packet["packet"].command.name.lower(), None)
        if not func:
            return None

        return func(serv, packet["packet"])

    def on_nscformatted(self, serv, packet):
        pass

    def on_nscattack(self, serv, packet):
        pass

    def on_xmlpacket(self, serv, packet):
        pass

    def on_login(self, serv, packet):
        response = smpacket.SMPacketServerNSCUOpts(
            packet=smpacket.SMOPacketServerLogin(
                approval=1,
                text="Succesfully Login"
            )
        )
        serv.send(response)

    def on_enterroom(self, serv, packet):
        pass

    def on_createroom(self, serv, packet):
        pass

    def on_roominfo(self, serv, packet):
        pass

