""" Base test for stepmania resources """

from smserver import server

from test import utils
from test.factories.connection_factory import ConnectionFactory



class ResourceTest(utils.DBTest):
    """ Base class for resource testing """

    def setUp(self):
        super().setUp()

        self.server = server.StepmaniaServer()

        self.connection = ConnectionFactory()
        self.token = self.connection.token

    def tearDown(self):
        super().tearDown()
