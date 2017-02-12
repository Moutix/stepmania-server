""" Module to test room model """

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
