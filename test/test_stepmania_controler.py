""" Test StepmaniaController module """

from smserver.stepmania_controller import StepmaniaController
from smserver.smutils import smconn
from smserver import server

from test import utils
from test.factories.connection_factory import ConnectionFactory
from test.factories.room_factory import RoomFactory
from test.factories.song_factory import SongFactory
from test.factories.user_factory import UserFactory


class StepmaniaControllerTest(utils.DBTest):
    """ Test Stepmania Server class """

    def setUp(self):
        super().setUp()

        self.server = server.StepmaniaServer()
        self.conn = smconn.StepmaniaConn(self.server, "8.8.8.8", 42)
        self.connection = ConnectionFactory(token=self.conn.token)

        self.controller = StepmaniaController(self.server, self.conn, None, self.session)

    def tearDown(self):
        super().tearDown()

    def test_connection(self):
        """ test getting the connection associated with the conn object"""

        self.assertEqual(self.controller.connection, self.connection)

        # Trying to reaccess it
        self.assertEqual(self.controller.connection, self.connection)

    def test_room(self):
        """ Test getting the room associated with a connection """

        self.assertEqual(self.controller.room, None)
        room = RoomFactory()
        self.connection.room = room
        self.session.commit()
        self.assertEqual(self.controller.room, room)

    def test_song(self):
        """ Test getting the song associated with a connection """

        self.assertEqual(self.controller.song, None)
        song = SongFactory()
        self.connection.song = song
        self.session.commit()
        self.assertEqual(self.controller.song, song)

    def test_users(self):
        """ Test getting the users associated with a connection """

        self.assertEqual(self.controller.users, [])
        user = UserFactory(connection=self.connection)
        self.assertEqual(self.controller.users, [user])
