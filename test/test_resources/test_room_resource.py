""" Test for room resource """

import hashlib

from smserver import exceptions
from smserver.resources.room_resource import RoomResource

from test.factories.user_factory import UserFactory
from test.test_resources import base

class RoomResourceTest(base.ResourceTest):
    """ Room resource class test """

    def setUp(self):
        super().setUp()

        self.resource = RoomResource(self.server, self.token, self.session)

    def test_create(self):
        """ Test room creation """

        # No user unauthorized
        with self.assertRaises(exceptions.Unauthorized):
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
