""" Test SMThread module """

import unittest
import mock

from smserver.smutils import smconn
from smserver.smutils import smthread


class BaseStepmaniaServerTest(unittest.TestCase):
    """ Test Stepmania Server class """

    def setUp(self):
        self.server = smthread.StepmaniaServer([])
        self.smthread = smconn.SMThread(self.server, "127.0.0.1", 888)
        self.server._servers.append(self.smthread) #pylint: disable=protected-access

        self.conn1 = smconn.StepmaniaConn(self.server, "8.8.8.8", 42)
        self.conn2 = smconn.StepmaniaConn(self.server, "8.8.8.9", 42)

    def tearDown(self):
        self.server.__init__([])
        self.server._servers.append(self.smthread) #pylint: disable=protected-access
        self.conn1 = smconn.StepmaniaConn(self.server, "8.8.8.8", 42)
        self.conn2 = smconn.StepmaniaConn(self.server, "8.8.8.9", 42)

    @mock.patch("threading.Thread.is_alive")
    def test_isalive(self, is_alive):
        """ test is_alive function """

        is_alive.return_value = True
        self.assertEqual(self.smthread.is_alive(), True)

        is_alive.return_value = False
        self.assertEqual(self.smthread.is_alive(), False)

    def test_connections(self):
        """ test listing the connections """

        self.assertEqual(list(self.server.connections), [])

        self.server.add_connection(self.conn1)
        self.assertEqual(list(self.server.connections), [self.conn1])

    def test_add_connection(self):
        """ test listing the connections """

        self.assertEqual(list(self.server.connections), [])

        self.server.add_connection(self.conn1)
        self.server.add_connection(self.conn2)
        self.assertIn(self.conn1, self.server.connections)
        self.assertIn(self.conn2, self.server.connections)

    def test_find_connection(self):
        """ Test finding a connection base on the token """

        self.server.add_connection(self.conn1)
        self.server.add_connection(self.conn2)
        self.assertEqual(self.server.find_connection(self.conn1.token), self.conn1)

    def test_add_to_room(self):
        """ Test adding a connection in a room """

        # Cannot add a unknown connection to a room
        self.server.add_to_room(self.conn1.token, 5)
        self.assertEqual(self.conn1.room, None)

        self.server.add_connection(self.conn1)
        self.server.add_to_room(self.conn1.token, 5)
        self.assertEqual(self.conn1.room, 5)
        self.assertIn(self.conn1, self.server.room_connections(5))

    def test_del_from_room(self):
        """ Test removing a connection from a room """

        self.server.add_connection(self.conn1)
        self.server.add_to_room(self.conn1.token, 5)
        self.assertEqual(self.conn1.room, 5)
        self.assertIn(self.conn1, self.server.room_connections(5))

        # Leave another room
        self.server.del_from_room(self.conn1.token, 4)
        self.assertEqual(self.conn1.room, 5)

        # Leave guess room
        self.server.del_from_room(self.conn1.token)
        self.assertEqual(self.conn1.room, None)

        self.server.add_to_room(self.conn1.token, 5)
        self.assertEqual(self.conn1.room, 5)

        # Leave correct room
        self.server.del_from_room(self.conn1.token, 5)
        self.assertEqual(self.conn1.room, None)

    @mock.patch("smserver.smutils.smconn.StepmaniaConn.send")
    def test_sendall(self, conn_send):
        """ test sending a packet to all conections """

        self.server.add_connection(self.conn1)
        self.server.add_connection(self.conn2)

        self.server.sendall("aaaa")
        self.assertEqual(conn_send.call_count, 2)
