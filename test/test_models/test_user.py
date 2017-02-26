""" Module to test user model """

from smserver import models

from test.factories import user_factory
from test import utils

class UserTest(utils.DBTest):
    """ test User model"""

    def test_fullname_without_room(self):
        """ Test user fullname """

        admin = user_factory.AdminFactory()
        self.assertEqual(admin.fullname(), "~%s" % admin.name)

        user = user_factory.UserFactory(rank=9)
        self.assertEqual(user.fullname(), "&%s" % user.name)

        user = user_factory.UserFactory(rank=4)
        self.assertEqual(user.fullname(), "@%s" % user.name)

        user = user_factory.UserFactory(rank=2)
        self.assertEqual(user.fullname(), "%%%s" % user.name)

        user = user_factory.UserFactory()
        self.assertEqual(user.fullname(), user.name)

    def test_fullname_with_room(self):
        """ Test user fullname with room """

        user = user_factory.user_with_room_privilege(level=10)

        self.assertEqual(user.fullname(user.room.id), "~%s" % user.name)

        user = user_factory.user_with_room_privilege(level=9)
        self.assertEqual(user.fullname(user.room.id), "&%s" % user.name)

        user = user_factory.user_with_room_privilege(level=4)
        self.assertEqual(user.fullname(user.room.id), "@%s" % user.name)

        user = user_factory.user_with_room_privilege(level=2)
        self.assertEqual(user.fullname(user.room.id), "%%%s" % user.name)

        user = user_factory.user_with_room_privilege()
        self.assertEqual(user.fullname(user.room.id), user.name)

    def test_level(self):
        """ Test user level """

        user = user_factory.user_with_room_privilege(level=5)
        room = user.room
        self.assertEqual(user.level(room.id), 5)

        user.rank = 9
        self.assertEqual(user.level(), 9)
        self.assertEqual(user.level(room.id), 5)

        user2 = user_factory.UserFactory(rank=4)
        self.assertEqual(user2.level(room.id), 1)

    def test_from_ids(self):
        """ Test getting the users from list of ids """

        self.assertEqual(models.User.from_ids([], self.session), [])

        user1 = user_factory.UserFactory()
        user2 = user_factory.UserFactory()

        users = models.User.from_ids([user1.id, user2.id], self.session)
        self.assertIn(user1, users)
        self.assertIn(user2, users)


        self.assertEqual(list(models.User.from_ids(["reg"], self.session)), [])

    def test_online_from_ids(self):
        """ Test getting the online users from list of ids """

        self.assertEqual(models.User.online_from_ids([], self.session), [])

        user1 = user_factory.UserFactory()
        user2 = user_factory.UserFactory()

        self.assertEqual(list(models.User.online_from_ids([user1.id, user2.id], self.session)), [])

        self.assertEqual(list(models.User.online_from_ids(["reg"], self.session)), [])

        user1.online = True
        self.session.commit()

        users = models.User.online_from_ids([user1.id, user2.id], self.session)
        self.assertIn(user1, users)
        self.assertNotIn(user2, users)

    def test_from_connection_token(self):
        """ Test getting the online users assiociated with a connection_token """

        self.assertEqual(models.User.from_connection_token(None, self.session), [])

        user1 = user_factory.UserFactory(online=True, connection_token="aa")
        user2 = user_factory.UserFactory(connection_token="aa")


        users = models.User.from_connection_token("aa", self.session)
        self.assertIn(user1, users)
        self.assertNotIn(user2, users)
