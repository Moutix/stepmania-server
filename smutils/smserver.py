#!/usr/bin/env python3
# -*- coding: utf8 -*-

import socket
from threading import Thread, Lock

from . import smpacket

class StepmaniaThread(Thread):
    def __init__(self, serv, conn, ip, port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self._serv = serv
        self._conn = conn

    def run(self):
        while True:
            try:
                self._on_data(self._conn.recv(1024))
            except socket.error:
                self._serv.on_disconnect(self)
                break

        with self._serv.mutex:
            self._serv.connections.remove(self)
        self._conn.close()

    def _on_data(self, data):
        packet = smpacket.SMPacket.parse_binary(data)
        if not packet:
            print("packet %s drop" % data)
            return None

        func = getattr(self._serv, "on_%s" % packet.command.name.lower(), None)
        if not func:
            print("No action for packet %s" % packet.command.name)
            return None

        func(self._serv, self, packet)

    def send(self, packet):
        self._conn.sendall(packet.binary)

class StepmaniaServer(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.mutex = Lock()
        self.connections = []
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self.ip, self.port))
        self._socket.listen(5)

    def start(self):
        while 1:
            conn, addr = self._socket.accept()
            thread = StepmaniaThread(self, conn, *addr)
            with self.mutex:
                self.connections.append(thread)
            thread.start()

    def on_disconnect(self, serv):
        pass

    def on_nscping(self, serv, packet):
        serv.send(smpacket.SMPacketServerNSCPingR())

    def on_nscpingr(self, serv, packet):
        pass

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
        func = getattr(self, "on_%s" % packet.opts["packet"].command.name.lower(), None)
        if not func:
            return None

        return func(serv, packet.opts["packet"])

    def on_nscformatted(self, serv, packet):
        pass

    def on_nscattack(self, serv, packet):
        pass

    def on_xmlpacket (self, serv, packet):
        pass

    def on_login(self, serv, packet):
        pass

    def on_enterroom(self, serv, packet):
        pass

    def on_createroom(self, serv, packet):
        pass

    def on_roominfo(self, serv, packet):
        pass

