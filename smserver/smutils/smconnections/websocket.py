#!/usr/bin/env python3
# -*- coding: utf8 -*-

import socket
import asyncio
import websockets

from smserver.smutils import smconn

class WebSocketClient(smconn.StepmaniaConn):
    ENCODING = "json"

    def __init__(self, serv, ip, port, websocket, path, loop):
        smconn.StepmaniaConn.__init__(self, serv, ip, port)
        self.websocket = websocket
        self.task = None
        self.loop = loop

    @asyncio.coroutine
    def run(self):
        while True:
            try:
                data = yield from self.websocket.recv()
            except websockets.ConnectionClosed:
                break

            self._on_data(data)

        self.close()

    def _send_data(self, data):
        self.loop.create_task(self.websocket.send(data))

    def close(self):
        self._serv.on_disconnect(self)
        self.websocket.close()

class WebSocketServer(smconn.SMThread):
    def __init__(self, server, ip, port):
        smconn.SMThread.__init__(self, server, ip, port)

        self.loop = asyncio.new_event_loop()

        self._serv = None
        self.server = server
        self.daemon = True
        self.ip = ip
        self.port = port
        self.clients = {}

    @asyncio.coroutine
    def _accept_client(self, websocket, path=""):
        ip, port = websocket.remote_address
        client = WebSocketClient(self.server, ip, port, websocket, path, self.loop)

        self.server.add_connection(client)
        try:
            yield from client.run()
        except Exception:
            client.close()
            raise

    def run(self):
        self._serv = self.loop.run_until_complete(
            websockets.serve(self._accept_client, self.ip, self.port, loop=self.loop))

        self.loop.run_forever()
        smconn.SMThread.run(self)

    def stop(self):
        smconn.SMThread.stop(self)

        if self._serv is None:
            return

        sockets = self._serv.server.sockets
        if sockets:
            for sock in sockets:
                sock.shutdown(socket.SHUT_RDWR)

        self.loop.stop()
        self._serv.close()

