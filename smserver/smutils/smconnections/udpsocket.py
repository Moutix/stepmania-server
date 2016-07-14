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


class UDPServer(smconn.SMThread):
    def __init__(self, server, ip, port):
        smconn.SMThread.__init__(self, server, ip, port)

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.ip, self.port))
        self._socket.settimeout(0.5)
        self._continue = True

    def run(self):
        while self._continue:
            try:
                data, addr = self._socket.recvfrom(8192)
            except socket.timeout:
                continue

            ip, port = addr

            SocketConn(self.server, ip, port, data).start()

        self._socket.close()
        smconn.SMThread.run(self)

    def stop(self):
        smconn.SMThread.stop(self)
        self._continue = False

