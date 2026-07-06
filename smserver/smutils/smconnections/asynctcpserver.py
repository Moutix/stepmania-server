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

    async def run(self):
        self.log.debug("Client run() started for %s:%s", self.ip, self.port)
        full_data = b''
        size = None
        data_left = b''

        while True:
            if data_left:
                data = data_left
                data_left = b""
            else:
                try:
                    self.log.debug("Waiting for data from %s:%s", self.ip, self.port)
                    data = await self.reader.read(8192)
                    self.log.debug("Received %d bytes from %s:%s", len(data), self.ip, self.port)
                except asyncio.CancelledError:
                    self.log.info("Client %s:%s cancelled", self.ip, self.port)
                    break

            if data == b'':
                self.log.info("Client %s:%s sent empty data (connection closed)", self.ip, self.port)
                break

            if not size:
                if len(data) < 5:
                    self.log.info("packet %s drop: to short", data)
                    continue

                full_data = data[:4]
                data = data[4:]
                size = int.from_bytes(full_data[:4], byteorder='big')
                self.log.debug("Packet size: %d bytes from %s:%s", size, self.ip, self.port)

            if len(data) < size - len(full_data):
                full_data += data
                self.log.debug("Incomplete packet, accumulated %d/%d bytes", len(full_data), size + 4)
                continue

            payload_size = len(full_data) - 4 + size
            full_data += data[:payload_size]

            self.log.debug("Processing complete packet of %d bytes from %s:%s", payload_size, self.ip, self.port)
            self._on_data(full_data)

            data_left = data[payload_size:]
            full_data = b""
            size = None

        self.log.info("Client run() ending for %s:%s", self.ip, self.port)
        self.close()

    def send_data(self, data):
        self.log.debug("Sending %d bytes to %s:%s", len(data), self.ip, self.port)
        self.writer.write(data)
        self.loop.create_task(self.writer.drain())

    def close(self):
        self.log.debug("Closing connection for %s:%s", self.ip, self.port)
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
        self.log.info("Client connecting from %s:%s", ip, port)
        client = AsyncSocketClient(self.server, ip, port, client_reader, client_writer, self.loop)

        task = self.loop.create_task(client.run())
        client.task = task
        self.clients[client.task] = client

        self.log.debug("Added client task for %s:%s", ip, port)
        self.server.add_connection(client)

        def client_done(task):
            self.log.debug("Client task done callback for %s:%s", ip, port)
            try:
                if not task.cancelled():
                    task.result()
            except Exception as e:
                self.log.error("Client task exception for %s:%s: %s", ip, port, e)
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
            asyncio.wait_for(self._serv.wait_closed(), timeout=1)
        )
        for task in self.clients:
            task.cancel()

        self.loop.run_until_complete(asyncio.gather(*self.clients))

    def stop(self):
        smconn.SMThread.stop(self)
        self.stop_server()
        self.loop.stop()
