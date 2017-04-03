""" Test the async tcp server connection """

import unittest
import socket

import asyncio
import mock

from smserver.smutils.smconnections import asynctcpserver

class AsyncSocketServerTest(unittest.TestCase):
    """ Test the thread which handle async tcp connection """

    def setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        self.ip, self.port = sock.getsockname()

        self.mock_server = mock.MagicMock()

        self.server = asynctcpserver.AsyncSocketServer(
            self.mock_server, self.ip, self.port, self.loop
        )

        self.reader, self.writer = None, None

    def tearDown(self):
        self.loop.close()
        self.mock_server.reset_mock()

    @asyncio.coroutine
    def client_connection(self):
        """ Coroutine to open the client connection """

        reader, writer = yield from asyncio.open_connection(
            self.ip, self.port, loop=self.loop
        )
        return reader, writer

    def start_client(self):
        """ Start the client """

        self.reader, self.writer = self.loop.run_until_complete(
            self.client_connection()
        )

    def start_server(self):
        """ Start the server """

        self.server.start_server()

    def stop_server(self):
        """ Stop the server """

        self.server.stop_server()

    def run_loop_once(self):
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()

    def test_server_close_while_client_connected(self):
        """ Try stopping the server during client connection """

        self.start_server()
        self.start_client()
        self.stop_server()
        self.mock_server.add_connection.assert_called_once()

    @mock.patch("smserver.smutils.smconnections.asynctcpserver.AsyncSocketClient._on_data")
    def test_valid_package(self, on_data):
        """ Test sending data to the server """

        self.start_server()
        self.start_client()
        self.mock_server.add_connection.assert_called_once()
        connection = self.mock_server.add_connection.call_args[0][0]

        self.writer.write(b"\x00\x00\x00\x01\x54")
        on_data.side_effect = connection.send_data

        data = self.loop.run_until_complete(self.reader.read(4096))

        self.assertEqual(data, b"\x00\x00\x00\x01\x54")
        on_data.assert_called_with(b"\x00\x00\x00\x01\x54")
        self.run_loop_once()

        self.stop_server()

    @mock.patch("smserver.smutils.smconnections.asynctcpserver.AsyncSocketClient._on_data")
    def test_double_valid_package(self, on_data):
        """ Test sending data to the server """

        self.start_server()
        self.start_client()
        self.mock_server.add_connection.assert_called_once()
        connection = self.mock_server.add_connection.call_args[0][0]

        self.writer.write(b"\x00\x00\x00\x01\x54\x00\x00\x00\x01\x55")

        on_data.side_effect = connection.send_data

        data = self.loop.run_until_complete(self.reader.read(4096))
        self.assertEqual(data, b"\x00\x00\x00\x01\x54\x00\x00\x00\x01\x55")

        self.assertEqual(on_data.call_count, 2)
        self.assertEqual(on_data.call_args_list[0][0][0], b"\x00\x00\x00\x01\x54")
        self.assertEqual(on_data.call_args_list[1][0][0], b"\x00\x00\x00\x01\x55")
        self.run_loop_once()

        self.stop_server()

    @mock.patch("smserver.smutils.smconnections.asynctcpserver.AsyncSocketClient._on_data")
    def test_invalid_package(self, on_data):
        """ Test sending data to the server """

        self.start_server()
        self.start_client()
        self.mock_server.add_connection.assert_called_once()
        self.writer.write(b"\x00\x00\x43")
        self.writer.write(b"\x00\x00\x00\x45")
        self.loop.run_until_complete(self.writer.drain())
        self.run_loop_once()

        on_data.assert_not_called()

        self.stop_server()
