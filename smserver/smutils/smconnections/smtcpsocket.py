#!/usr/bin/env python3
# -*- coding: utf8 -*-

import socket
from threading import Thread

from smserver.smutils import smconn, smpacket

class SocketConn(smconn.StepmaniaConn):
    def received_data(self):
        full_data = b""
        size = None
        data_left = b""

        while True:
            if len(data_left) > 0:
                data = data_left
                data_left = b""
            else:
                try:
                    data = self._conn.recv(8192)
                except socket.error:
                    yield None
                    continue

            if data == b'':
                yield None
                continue

            if not size:
                if len(data) < 5:
                    self.logger.info("packet %s drop: to short" % (data))
                    continue

                full_data = data[:4]
                data = data[4:]
                size = int.from_bytes(full_data[:4], byteorder='big')

            if len(data) < size - len(full_data):
                full_data += data
                continue

            payload_size = len(full_data) - 4 + size
            full_data += data[:payload_size]

            yield full_data

            data_left = data[payload_size:]
            full_data = b""
            size = None

    def _on_data(self, data):
        packet = smpacket.SMPacket.parse_binary(data)
        if not packet:
            self.logger.info("packet %s drop from %s" % (data, self.ip))
            return None

        self.logger.debug("Packet received from %s: %s" % (self.ip, packet))

        self._serv.on_packet(self, packet)

    def send(self, packet):
        self.logger.debug("packet send to %s: %s" % (self.ip, packet))
        with self.mutex:
            try:
                self._conn.sendall(packet.binary)
            except OSError:
                self._serv.on_disconnect(self)
                self._conn.close()

class SocketServer(Thread):
    def __init__(self, server, ip, port):
        Thread.__init__(self)

        self.server = server
        self.ip = ip
        self.port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.ip, self.port))
        self._socket.listen(5)

    def run(self):
        while 1:
            conn, addr = self._socket.accept()
            thread = SocketConn(self.server, conn, *addr)
            self.server.add_connection(thread)
            thread.start()

