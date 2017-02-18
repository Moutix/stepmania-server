""" Test for user resource """

import hashlib

from smserver import exceptions
from smserver import models
from smserver.resources.user_resource import UserResource

from test.factories.user_factory import UserFactory
from test.test_resources import base

class UserResourceTest(base.ResourceTest):
    """ User resource class test """

    def setUp(self):
        super().setUp()

        self.resource = UserResource(self.server, self.token, self.session)

    def test_create(self):
        """ Test user creation """

        # password too short
        with self.assertRaises(exceptions.ValidationError):
            self.resource.create("name", "pass")

        # Rank too high
        with self.assertRaises(exceptions.Unauthorized):
            self.resource.create("name", "password", rank=10)

        user = self.resource.create("User 1", "Password", email="test@test.io")

        password = hashlib.sha256("Password".encode('utf-8')).hexdigest()

        self.assertEqual(user, self.session.query(models.User).filter_by(name="User 1").first())
        self.assertEqual(user.email, "test@test.io")
        self.assertEqual(user.password, password)
        self.assertEqual(user.rank, 1)

        # User already created
        with self.assertRaises(exceptions.ValidationError):
            self.resource.create("User 1", "password")

    def test_login(self):
        """ Test login an user """

        user = UserFactory(
            name="User 1",
            password=hashlib.sha256("Password".encode('utf-8')).hexdigest()
        )

        # Short password
        with self.assertRaises(exceptions.Forbidden):
            self.resource.login("User 1", "pass")

        # Wrong password
        with self.assertRaises(exceptions.Forbidden):
            self.resource.login("User 1", "Wrong password")

        # Wrong user
        with self.assertRaises(exceptions.Forbidden):
            self.resource.login("User 2", "Password")

        self.assertEqual(user, self.resource.login("User 1", "Password"))

        models.Ban.ban(session=self.session, user_id=user.id)
        # User Ban
        with self.assertRaises(exceptions.Forbidden):
            self.resource.login("User 1", "Password")

    def test_login_or_create(self):
        """ Test login or create an User"""

        password = hashlib.sha256("Password".encode('utf-8')).hexdigest()

        user = UserFactory(
            name="User 1",
            password=password
        )

        # Short password
        with self.assertRaises(exceptions.Forbidden):
            self.resource.login_or_create("User 1", "pass")

        # Wrong password
        with self.assertRaises(exceptions.Forbidden):
            self.resource.login_or_create("User 1", "Wrong password")

        # Login
        self.assertEqual(user, self.resource.login_or_create("User 1", "Password"))

        # Create
        user2 = self.resource.login_or_create("User 2", "Password")
        self.assertEqual(user2, self.session.query(models.User).filter_by(name="User 2").first())
        self.assertEqual(user2.password, password)
        self.assertEqual(user2.rank, 1)

    def test_connection(self):
        """ Test user connection """

        user = UserFactory(online=True)
        with self.assertRaises(exceptions.Unauthorized):
            self.resource.connect(user, pos=0)

        user = UserFactory()
        self.server.config.server["max_users"] = -1

        self.assertEqual(self.resource.connect(user, pos=1), user)
        self.assertEqual(user.pos, 1)
        self.assertTrue(user.online)
        self.assertEqual(user.connection, self.connection)
        self.assertIsNone(user.room)

        self.resource.connect(user, pos=0)
        self.assertEqual(user.pos, 0)
        self.assertTrue(user.online)
        self.assertEqual(user.connection, self.connection)
        self.assertIsNone(user.room)


        user2 = UserFactory()

        self.server.config.server["max_users"] = 1
        with self.assertRaises(exceptions.Unauthorized):
            self.resource.connect(user, pos=1)

        self.server.config.server["max_users"] = -1

        # User2 connect in a new position
        self.resource.connect(user2, pos=1)
        self.assertEqual(user2.pos, 1)
        self.assertTrue(user2.online)
        self.assertEqual(user2.connection, self.connection)
        self.assertIsNone(user2.room)
        self.assertEqual(len(self.connection.active_users), 2)

        # User2 connect at the user1 position
        self.resource.connect(user2, pos=0)
        self.assertEqual(user2.pos, 0)
        self.assertTrue(user2.online)
        self.assertFalse(user.online)
        self.assertEqual(user2.connection, self.connection)
        self.assertIsNone(user2.room)

        self.assertEqual(len(self.connection.users), 2)
        self.assertEqual(len(self.connection.active_users), 1)
