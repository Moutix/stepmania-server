""" Module to test connection model """


import sqlalchemy

from smserver import models

from test.factories.connection_factory import ConnectionFactory
from test import utils

class ConnectionTest(utils.DBTest):
    """ test User model"""

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
