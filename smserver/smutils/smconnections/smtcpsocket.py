#!/usr/bin/env python3
# -*- coding: utf8 -*-

import socket
from threading import Thread

from smserver.smutils import smconn

class SocketConn(smconn.StepmaniaConn, Thread):
    ENCODING = "binary"

    def __init__(self, serv, ip, port, conn):
        Thread.__init__(self)
        smconn.StepmaniaConn.__init__(self, serv, ip, port)
        self._conn = conn

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

    def _send_data(self, data):
        with self.mutex:
            try:
                self._conn.sendall(data)
            except OSError:
                self.close()

    def close(self):
        self._conn.close()
        smconn.StepmaniaConn.close(self)

class SocketServer(smconn.SMThread):
    def __init__(self, server, ip, port):
        smconn.SMThread.__init__(self, server, ip, port)

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.ip, self.port))
        self._socket.listen(5)
        self._continue = True
        self._connections = []

    def run(self):
        while self._continue:
            try:
                conn, addr = self._socket.accept()
            except socket.error:
                self._socket.close()
                break

            ip, port = addr
            thread = SocketConn(self.server, ip, port, conn)
            self.server.add_connection(thread)
            thread.start()

        smconn.SMThread.run(self)

    def stop(self):
        smconn.SMThread.stop(self)
        self._continue = False
        self._socket.shutdown(socket.SHUT_RDWR)

