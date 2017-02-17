""" Module to test room model """

import hashlib

from smserver import models

from test.factories.user_factory import UserFactory, user_with_room_privilege
from test.factories.room_factory import RoomFactory
from test import utils

class RoomTest(utils.DBTest):
    """ test Room model"""

    def test_nb_players(self):
        """ Test getting the number of user in the room """

        room = RoomFactory()

        self.assertEqual(room.nb_players, 0)
        UserFactory(room=room, online=True)
        self.session.commit()

        self.assertEqual(room.nb_players, 1)

    def test_online_users(self):
        """ Test getting the online users in the room """

        room = RoomFactory()

        self.assertEqual(list(room.online_users), [])
        user1 = UserFactory(room=room, online=True)
        user2 = UserFactory(room=room, online=True)
        self.session.commit()

        online_users = list(room.online_users)

        self.assertEqual(len(online_users), 2)
        self.assertIn(user1, online_users)
        self.assertIn(user2, online_users)

    def test_moderators(self):
        """ Test getting the list of moderators in the room """

        room = RoomFactory()
        user_with_room_privilege(level=1, room=room)
        self.assertEqual(list(room.moderators), [])

        mod1 = user_with_room_privilege(level=6, room=room)
        mod2 = user_with_room_privilege(level=10, room=room)

        moderators = list(room.moderators)

        self.assertEqual(len(moderators), 2)
        self.assertIn(mod1, moderators)
        self.assertIn(mod2, moderators)

    def test_is_full(self):
        """ Test checking if the room is full """

        room = RoomFactory(max_users=2)
        self.assertEqual(room.is_full(), False)

        UserFactory(room=room, online=True)
        UserFactory(room=room, online=True)
        self.session.commit()
        self.assertEqual(room.is_full(), True)


    def test_login(self):
        """ Test login in a room """

        self.assertIsNone(
            models.Room.login("name", "pass", self.session)
        )

        # Room without password
        room = RoomFactory(name="Room 1")

        self.assertEqual(
            models.Room.login("Room 1", None, self.session),
            room
        )
        self.assertEqual(
            models.Room.login("Room 1", "password", self.session),
            room
        )

        # Room with password
        password = hashlib.sha256("pass".encode('utf-8')).hexdigest()
        room = RoomFactory(name="Room 2", password=password)

        self.assertIsNone(
            models.Room.login("Room 2", "Wrong password", self.session)
        )

        self.assertEqual(
            models.Room.login("Room 2", "pass", self.session),
            room
        )

    def test_available_rooms(self):
        """ Test getting the available rooms for a given user """

        self.assertEqual(models.Room.available_rooms(self.session).count(), 0)

        room = RoomFactory(hidden=False, name="Room classic")
        room_hidden = RoomFactory(hidden=True, name="Room hidden")
        user = UserFactory(rank=5)

        rooms = list(models.Room.available_rooms(self.session, user))

        self.assertEqual(len(rooms), 2)
        self.assertIn(room, rooms)
        self.assertIn(room_hidden, rooms)

        user = UserFactory()
        rooms = list(models.Room.available_rooms(self.session, user))
        self.assertEqual(len(rooms), 1)
        self.assertIn(room, rooms)
        self.assertNotIn(room_hidden, rooms)

        user2 = user_with_room_privilege(room=room_hidden, level=2)
        rooms = list(models.Room.available_rooms(self.session, user2))
        self.assertEqual(len(rooms), 2)
        self.assertIn(room, rooms)
        self.assertIn(room_hidden, rooms)
