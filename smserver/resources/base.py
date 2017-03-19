""" Module which contains the base structure of all the resources"""

from sqlalchemy.orm import object_session

from smserver import models

class BaseResource(object):
    """ Inherit from this class to create a new resource """

    def __init__(self, serv, token=None, session=None, connection=None):
        self.serv = serv
        if not token and not connection:
            raise TypeError("Need to provide a token or a connection")

        self._connection = connection
        if connection:
            token = connection.token
            session = object_session(connection)

        self.token = token
        self.session = session

        self.log = self.serv.log


    @property
    def connection(self):
        """ The connection object in the database """

        if self._connection:
            return self._connection

        self._connection = models.Connection.by_token(self.token, self.session)
        return self._connection
