#!/usr/bin/env python3
# -*- coding: utf8 -*-

import socket

import asyncio
import asyncio.streams

from smserver.smutils import smconn

class AsyncSocketClient(smconn.StepmaniaConn):
    ENCODING = "binary"

    def __init__(self, serv, ip, port, reader, writer, loop):
        smconn.StepmaniaConn.__init__(self, serv, ip, port)
        self.reader = reader
        self.writer = writer
        self.task = None
        self.loop = loop

    @asyncio.coroutine
    def run(self):
        full_data = b''
        size = None
        data_left = b''

        while True:
            if len(data_left) > 0:
                data = data_left
                data_left = b""
            else:
                data = (yield from self.reader.read(8192))

            if data == b'':
                break

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

            self._on_data(full_data)

            data_left = data[payload_size:]
            full_data = b""
            size = None

        self.close()

    def _send_data(self, data):
        self.writer.write(data)
        self.loop.create_task(self.writer.drain())

    def close(self):
        self._serv.on_disconnect(self)
        self.writer.close()

class AsyncSocketServer(smconn.SMThread):
    def __init__(self, server, ip, port):
        smconn.SMThread.__init__(self, server, ip, port)

        self.loop = asyncio.new_event_loop()
        self._serv = None
        self.clients = {}

    def _accept_client(self, client_reader, client_writer):
        ip, port = client_writer.get_extra_info("peername")
        client = AsyncSocketClient(self.server, ip, port, client_reader, client_writer, self.loop)

        task = asyncio.Task(client.run(), loop=self.loop)
        client.task = task
        self.clients[client.task] = client

        self.server.add_connection(client)

        def client_done(task):
            self.clients[task].close()
            del self.clients[task]

        client.task.add_done_callback(client_done)

    def run(self):
        self._serv = self.loop.run_until_complete(
            asyncio.streams.start_server(self._accept_client,
                                         self.ip, self.port,
                                         loop=self.loop))
        self.loop.run_forever()
        self.loop.close()
        smconn.SMThread.run(self)

    def stop(self):
        smconn.SMThread.stop(self)

        if self._serv is None:
            return

        if self._serv.sockets:
            for sock in self._serv.sockets:
                sock.shutdown(socket.SHUT_RDWR)

        self.loop.stop()
        self._serv.close()

