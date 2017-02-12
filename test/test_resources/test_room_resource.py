""" Test for room resource """

import hashlib

import mock

from smserver import exceptions
from smserver.resources.room_resource import RoomResource

from test.factories.user_factory import UserFactory, user_with_room_privilege
from test.factories.room_factory import RoomFactory
from test.test_resources import base

class RoomResourceTest(base.ResourceTest):
    """ Room resource class test """

    def setUp(self):
        super().setUp()

        self.resource = RoomResource(self.server, self.token, self.session)

    def test_create(self):
        """ Test room creation """

        # No user unauthorized
        with self.assertRaises(exceptions.Forbidden):
            self.resource.create("aaa")

        user1 = UserFactory(connection=self.connection, online=True)
        user2 = UserFactory(connection=self.connection, online=True)

        room = self.resource.create("Room 1", description="description")
        self.assertIsNotNone(room)
        self.assertEqual(room.password, None)
        self.assertEqual(room.description, "description")
        self.assertEqual(room.name, "Room 1")

        self.assertEqual(user1.level(room.id), 10)
        self.assertEqual(user2.level(room.id), 10)

        with self.assertRaises(exceptions.ValidationError):
            self.resource.create("Room 1")

    def test_create_with_password(self):
        """ Test create a room with a password """

        UserFactory(connection=self.connection, online=True)
        UserFactory(connection=self.connection, online=True)

        room = self.resource.create("Room 1", password="éàç")

        password = hashlib.sha256("éàç".encode('utf-8')).hexdigest()


        self.assertIsNotNone(room)
        self.assertEqual(room.password, password)
        self.assertEqual(room.name, "Room 1")

    def test_get_room(self):
        """ Test getting a room given his ID """

        with self.assertRaises(exceptions.NotFound):
            self.resource.get(4)

        room = RoomFactory()
        self.assertEqual(room, self.resource.get(room.id))

    @mock.patch("smserver.server.StepmaniaServer.add_to_room")
    @mock.patch("smserver.server.StepmaniaServer.del_from_room")
    def test_enter_room(self, del_from_room, add_to_room):
        """ Test enter in a room """

        room = RoomFactory()
        user = UserFactory(connection=self.connection, online=True)

        self.resource.enter(room)

        self.assertEqual(self.connection.room, room)
        self.assertEqual(user.room, room)
        del_from_room.assert_not_called()
        add_to_room.assert_called_with(self.token, room.id)

        add_to_room.reset_mock()

        room2 = RoomFactory()
        self.resource.enter(room2)

        self.assertEqual(self.connection.room, room2)
        self.assertEqual(user.room, room2)
        del_from_room.assert_called_with(self.token, room.id)
        add_to_room.assert_called_with(self.token, room2.id)

    @mock.patch("smserver.server.StepmaniaServer.add_to_room")
    @mock.patch("smserver.server.StepmaniaServer.del_from_room")
    def test_enter_room_unauthorized(self, del_from_room, add_to_room):
        """ Test enter in a room """


        room = RoomFactory()
        # No user unauthorized
        with self.assertRaises(exceptions.Forbidden):
            self.resource.enter(room)

        user_with_room_privilege(room=room, level=0, connection=self.connection, online=True)

        # User with insufficient right
        with self.assertRaises(exceptions.Forbidden):
            self.resource.enter(room)

        #Room full
        room = RoomFactory()
        room.max_users = 2
        UserFactory(room=room, online=True)
        UserFactory(room=room, online=True)
        with self.assertRaises(exceptions.Unauthorized):
            self.resource.enter(room)

        del_from_room.assert_not_called()
        add_to_room.assert_not_called()

    @mock.patch("smserver.server.StepmaniaServer.del_from_room")
    def test_leave_room(self, del_from_room):
        """ Test enter in a room """

        room = self.resource.leave()
        self.assertIsNone(room)
        del_from_room.assert_not_called()

        room = RoomFactory()
        user = UserFactory(connection=self.connection, online=True, room=room)
        self.connection.room = room

        self.assertEqual(self.resource.leave(), room)
        self.assertIsNone(user.room)
        self.assertIsNone(self.connection.room)
