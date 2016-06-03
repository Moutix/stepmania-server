#!/usr/bin/env python3
# -*- coding: utf8 -*-

import socket
import datetime
import logging
import time
from threading import Thread, Lock

from smserver.smutils import smpacket

class StepmaniaThread(Thread):
    _FPS = 60
    logger = logging.getLogger('stepmania')

    def __init__(self, serv, conn, ip, port):
        Thread.__init__(self)
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
        self._conn = conn

        self.logger.info("New connection: %s on port %s" % (ip, port))

    def run(self):
        while True:
            try:
                data = self.received_data()
            except socket.error:
                self._serv.on_disconnect(self)
                break

            self._on_data(data)

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
        self._connections = []
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.ip, self.port))
        self._socket.listen(5)

    def start(self):
        while 1:
            conn, addr = self._socket.accept()
            thread = StepmaniaThread(self, conn, *addr)
            with self.mutex:
                self._connections.append(thread)
            thread.start()

    @property
    def connections(self):
        with self.mutex:
            return self._connections

    def room_connections(self, room_id):
        for conn in self.connections:
            if conn.room != room_id:
                continue

            yield conn

    def player_connections(self, room_id, song_id):
        for conn in self.room_connections(room_id):
            if not conn.songs.get(song_id):
                continue

            yield conn

    def sendall(self, packet):
        for conn in self.connections:
            conn.send(packet)

    def sendroom(self, room_id, packet):
        for conn in self.room_connections(room_id):
            conn.send(packet)

    def sendplayers(self, room_id, song_id, packet):
        for conn in self.player_connections(room_id, song_id):
            conn.send(packet)

    def on_disconnect(self, serv):
        with self.mutex:
            self._connections.remove(serv)

    def on_packet(self, serv, packet):
        PacketHandler(self, serv, packet).handle()


class PacketHandler(object):
    def __init__(self, server, conn, packet):
        self.server = server
        self.packet = packet
        self.conn = conn

    def handle(self):
        func = getattr(self, "on_%s" % self.packet.command.name.lower(), None)
        if not func:
            return None

        func()

    def on_nscping(self):
        self.conn.send(smpacket.SMPacketServerNSCPingR())

    def on_nscpingr(self):
        with self.conn.mutex:
            self.conn.last_ping = datetime.datetime.now()

    def on_nschello(self):
        self.conn.send(smpacket.SMPacketServerNSCHello(version=128, name="Stepmania-Server"))

    def on_nscgsr(self):
        pass

    def on_nscgon(self):
        pass

    def on_nscgsu(self):
        pass

    def on_nscsu(self):
        pass

    def on_nsccm(self):
        pass

    def on_nscrsg(self):
        pass

    def on_nsccuul(self):
        pass

    def on_nsscsms(self):
        pass

    def on_nscuopts(self):
        pass

    def on_nssmonl(self):
        PacketHandler(self.server, self.conn, self.packet["packet"]).handle()

    def on_nscformatted(self):
        pass

    def on_nscattack(self):
        pass

    def on_xmlpacket(self):
        pass

    def on_login(self):
        response = smpacket.SMPacketServerNSCUOpts(
            packet=smpacket.SMOPacketServerLogin(
                approval=1,
                text="Succesfully Login"
            )
        )
        self.conn.send(response)

    def on_enterroom(self):
        pass

    def on_createroom(self):
        pass

    def on_roominfo(self):
        pass

    def send(self, packet):
        self.conn.send(packet)

    def sendall(self, packet):
        self.server.sendall(packet)

    def sendroom(self, room, packet):
        self.server.sendroom(room, packet)

