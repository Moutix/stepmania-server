""" Asyncio client module """

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
            if data_left:
                data = data_left
                data_left = b""
            else:
                try:
                    data = yield from self.reader.read(8192)
                except asyncio.CancelledError:
                    break

            if data == b'':
                break

            if not size:
                if len(data) < 5:
                    self.log.info("packet %s drop: to short", data)
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

    def send_data(self, data):
        self.writer.write(data)
        self.loop.create_task(self.writer.drain())

    def close(self):
        self._serv.on_disconnect(self)
        self.writer.close()


class AsyncSocketServer(smconn.SMThread):
    def __init__(self, server, ip, port, loop=None):
        smconn.SMThread.__init__(self, server, ip, port)

        self.loop = loop or asyncio.new_event_loop()
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
        self.start_server()
        self.loop.run_forever()
        self.loop.close()
        smconn.SMThread.run(self)

    def start_server(self):
        """ Start the server in the given loop """

        self._serv = self.loop.run_until_complete(asyncio.start_server(
            self._accept_client,
            host=self.ip,
            port=self.port,
            loop=self.loop,
        ))
        return self._serv

    def stop_server(self):
        """ Stop the server in the given loop """

        if self._serv is None:
            return

        if self._serv.sockets:
            for sock in self._serv.sockets:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass

        self._serv.close()
        self.loop.run_until_complete(
            asyncio.wait_for(self._serv.wait_closed(), timeout=1, loop=self.loop)
        )
        for task in self.clients:
            task.cancel()

        self.loop.run_until_complete(asyncio.gather(*self.clients))

    def stop(self):
        smconn.SMThread.stop(self)
        self.stop_server()
        self.loop.stop()
