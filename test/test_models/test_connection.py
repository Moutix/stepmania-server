""" Module to test connection model """


from smserver import models

from test.factories.connection_factory import ConnectionFactory
from test import utils

class ConnectionTest(utils.DBTest):
    """ test User model"""

    def test_remove(self):
        """ Test remove connection """

        models.Connection.remove("efz", self.session)

        self.assertEqual(self.session.query(models.Connection).count(), 0)

        conn = ConnectionFactory()
        self.assertEqual(self.session.query(models.Connection).count(), 1)

        models.Connection.remove(conn.token, self.session)
        self.assertEqual(self.session.query(models.Connection).count(), 0)
