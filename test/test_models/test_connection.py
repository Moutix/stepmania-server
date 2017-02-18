""" Module to test connection model """

import datetime

import sqlalchemy

from smserver import ability
from smserver import models

from test.factories.connection_factory import ConnectionFactory
from test.factories.user_factory import user_with_room_privilege, UserFactory
from test import utils

class ConnectionTest(utils.DBTest):
    """ test User model"""

    def test_alive(self):
        """ Test if a connectio is alive """

        connection = ConnectionFactory()
        self.assertTrue(connection.alive)

        connection.close_at = datetime.datetime.utcnow()
        self.assertFalse(connection.alive)

    def test_remove(self):
        """ Test remove connection """

        self.session.query(models.Connection).delete()

        models.Connection.remove("efz", self.session)

        self.assertEqual(self.session.query(models.Connection).count(), 0)

        conn = ConnectionFactory()
        self.assertEqual(self.session.query(models.Connection).count(), 1)

        models.Connection.remove(conn.token, self.session)
        self.assertEqual(self.session.query(models.Connection).count(), 0)

    def test_by_token(self):
        """ Test getting an object given his token """

        self.assertEqual(models.Connection.by_token("aa", self.session), None)

        ConnectionFactory()
        conn = ConnectionFactory()
        self.assertEqual(models.Connection.by_token(conn.token, self.session), conn)

    def test_create(self):
        """ Test connection creation """

        conn = models.Connection.create(self.session, ip="aaa", token="bbb")
        self.assertEqual(
            self.session.query(models.Connection).filter_by(token='bbb').first(),
            conn
        )

        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            models.Connection.create(self.session, ip="aaa")


    def test_active_users(self):
        """ Test getting the active users in a connection """
        conn = ConnectionFactory()
        self.assertEqual(conn.active_users, [])

        user1 = UserFactory(connection=conn, online=True)
        user2 = UserFactory(connection=conn, online=False)

        self.assertEqual(conn.active_users, [user1])

        user3 = UserFactory(connection=conn, online=True)

        self.assertEqual(len(conn.active_users), 2)
        self.assertIn(user1, conn.active_users)
        self.assertIn(user3, conn.active_users)
        self.assertNotIn(user2, conn.active_users)

    def test_level(self):
        """ Test getting the level of a connection  """

        conn = ConnectionFactory()
        self.assertEqual(conn.level(), 0)

        user = user_with_room_privilege(level=2, connection=conn, online=True)
        room = user.room
        user_with_room_privilege(level=5, connection=conn, online=False, room=room)

        self.assertEqual(conn.level(room.id), 2)

    def test_can(self):
        """ Test connection can """

        conn = ConnectionFactory()
        self.assertEqual(conn.can(ability.Permissions.delete_room), False)

        user = user_with_room_privilege(level=10, connection=conn, online=True)
        room = user.room
        self.assertEqual(conn.can(ability.Permissions.delete_room, room.id), True)
