""" Module which contains the base structure of all the resources"""

from smserver import models

class BaseResource(object):
    """ Inherit from this class to create a new resource """

    def __init__(self, serv, token, session=None):
        self.serv = serv
        self.token = token
        self.session = session

        self.log = self.serv.log

        self._connection = None

    @property
    def connection(self):
        """ The connection object in the database """

        if self._connection:
            return self._connection

        self._connection = models.Connection.by_token(self.token, self.session)
        return self._connection
