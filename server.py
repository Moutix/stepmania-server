#!/usr/bin/env python3
# -*- coding: utf8 -*-

import socket
import smpacket
from threading import Thread, Lock

class on_smcommand(object):
    mapping = {}
    
    def __init__(self, command):
        self.command = command

    def __call__(self, f):
        self.mapping[self.command] = f
        def wrapped_f(*args):
            f(*args)

        return wrapped_f

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
                self._on_disconnect()
                break

        with self._serv.mutex:
            self._serv.connections.remove(self)
        self._conn.close()

    def _on_data(self, data):
        packet = smpacket.SMPacket.parse_binary(data)
        if not packet:
            print("packet %s drop" % data)
            return None

        func = on_smcommand.mapping.get(packet.command)
        if not func:
            print("No action for packet %s" % packet.command.name)
            return None

        func(self._serv, self, packet)

    def send(self, packet):
        self._conn.sendall(packet.binary)

    def _on_disconnect(self):
        print("Addr: %s disconnected" % self.ip)

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

    @on_smcommand(smpacket.SMClientCommand.NSCHello)
    def on_hello(self, serv, packet):
        serv.send(smpacket.SMPacketServerNSCHello(version=128, name="Ah que coucou"))

