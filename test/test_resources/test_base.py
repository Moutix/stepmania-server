""" Test the base resource """

from smserver.resources.base import BaseResource

from test.test_resources import base

class BaseResourceTest(base.ResourceTest):
    """ Base resource class test """

    def test_initialization(self):
        """ Tet base resource initialisation """

        with self.assertRaises(TypeError):
            BaseResource(self.server, session=self.session)

        resource = BaseResource(self.server, token=self.token, session=self.session)

        self.assertEqual(resource.connection, self.connection)
        self.assertEqual(resource.token, self.token)
        self.assertEqual(resource.session, self.session)

        resource = BaseResource(self.server, connection=self.connection)
        self.assertEqual(resource.connection, self.connection)
        self.assertEqual(resource.token, self.token)
        self.assertEqual(resource.session, self.session)
