""" Websocket client module """

import socket
import asyncio
import websockets

from smserver.smutils import smconn

class WebSocketClient(smconn.StepmaniaConn):
    ENCODING = "json"

    def __init__(self, serv, ip, port, websocket, _path, loop):
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

    def send_data(self, data):
        self.loop.create_task(self.websocket.send(data))

    def close(self):
        self._serv.on_disconnect(self)
        self.websocket.close()

class WebSocketServer(smconn.SMThread):
    def __init__(self, server, ip, port, loop=None):
        smconn.SMThread.__init__(self, server, ip, port)

        self.loop = loop or asyncio.new_event_loop()

        self._serv = None
        self.server = server
        self.daemon = True
        self.ip = ip
        self.port = port

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
        self.start_server()
        self.loop.run_forever()
        smconn.SMThread.run(self)

    def start_server(self):
        """ Start the websocket server """

        self._serv = self.loop.run_until_complete(
            websockets.serve(
                self._accept_client,
                host=self.ip,
                port=self.port,
                loop=self.loop,
            )
        )
        return self._serv

    def stop_server(self):
        """ Stop the server in the given loop """

        if self._serv is None:
            return

        sockets = self._serv.server.sockets
        if sockets:
            for sock in sockets:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass

        self._serv.close()
        self.loop.run_until_complete(
            asyncio.wait_for(self._serv.wait_closed(), timeout=1)
        )

    def stop(self):
        smconn.SMThread.stop(self)
        self.stop_server()
        self.loop.stop()
