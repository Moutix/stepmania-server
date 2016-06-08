#!/usr/bin/env python3
# -*- coding: utf8 -*-

from threading import Thread
import asyncio
import websockets

from smserver.smutils import smconn, smpacket

class WebSocketClient(smconn.StepmaniaConn):
    ENCODING = "json"

    def __init__(self, serv, ip, port, websocket, loop):
        smconn.StepmaniaConn.__init__(self, serv, ip, port)
        self.websocket = websocket
        self.task = None
        self.loop = loop

    @asyncio.coroutine
    def run(self):
        while True:
            data = yield from self.websocket.recv()
            self._on_data(data)

        self.close()

    def _send_data(self, data):
        self.loop.create_task(self.websocket.send(data))

    def close(self):
        self._serv.on_disconnect(self)
        self.websocket.close()

class WebSocketServer(Thread):
    def __init__(self, server, ip, port):
        Thread.__init__(self)

        self.loop = asyncio.get_event_loop()

        self._serv = None
        self.server = server
        self.ip = ip
        self.port = port
        self.clients = {}

    def _accept_client(self, websocket, path):
        ip, port = websocket.remode_address
        client = WebSocketClient(self.server, ip, port, websocket, self.loop)

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
            websockets.serve(self._accept_client, self.ip, self.port, loop=self.loop))

        self.loop.run_forever()


    def stop(self):
        if self._serv is not None:
            self._serv.close()
            self.loop.run_until_complete(self._serv.wait_closed())
            self._serv = None

