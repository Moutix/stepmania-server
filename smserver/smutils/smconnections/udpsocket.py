#!/usr/bin/env python3
# -*- coding: utf8 -*-

import socket
from threading import Thread

from smserver.smutils import smconn, smpacket

class SocketConn(smconn.StepmaniaConn, Thread):
    ENCODING = "binary"
    ALLOWED_PACKET = [smpacket.SMClientCommand.NSCFormatted]

    def __init__(self, serv, ip, port, data):
        Thread.__init__(self)
        smconn.StepmaniaConn.__init__(self, serv, ip, port)
        self._data = data

    def received_data(self):
        yield self._data

    def _send_data(self, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.sendto(data, (self.ip, self.port))

    def close(self):
        pass


class UDPServer(Thread):
    def __init__(self, server, ip, port):
        Thread.__init__(self)

        self.server = server
        self.ip = ip
        self.port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.ip, self.port))

    def run(self):
        while 1:
            data, addr = self._socket.recvfrom(8192)
            ip, port = addr

            SocketConn(self.server, ip, port, data).run()

