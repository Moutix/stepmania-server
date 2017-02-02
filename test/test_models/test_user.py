""" Module to test user model """

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
        self.assertEqual(user.level(user.room.id), 5)

        user.rank = 9
        self.assertEqual(user.level(), 9)
