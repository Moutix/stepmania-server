""" Connection models """

import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from smserver.models import schema
from smserver import ability

__all__ = ['Connection']

class Connection(schema.Base):
    """ Connection Model, it representes a true connection on the server
    The data associated with the connection are store locally for performance issue.
    """

    __tablename__ = 'connections'

    id             = Column(Integer, primary_key=True)
    token          = Column(String(255), index=True, unique=True, nullable=False)

    ip             = Column(String(255))
    port           = Column(Integer)

    client_name    = Column(String(255))
    client_version = Column(String(255))

    users          = relationship("User", back_populates="connection")

    room_id        = Column(Integer, ForeignKey('rooms.id'))
    room           = relationship("Room", back_populates="connections")

    song_id        = Column(Integer, ForeignKey('songs.id'))
    song           = relationship("Song")

    created_at     = Column(DateTime, default=datetime.datetime.now)
    updated_at     = Column(DateTime, onupdate=datetime.datetime.now)
    close_at       = Column(DateTime)

    def __repr__(self):
        return "<Connection #%s (ip='%s', port='%s')>" % (
            self.token, self.ip, self.port)

    @property
    def alive(self):
        """ Return true if the connection is still active """
        return not bool(self.close_at)

    @classmethod
    def remove(cls, token, session):
        """ Remove the connection """

        return (session
                .query(cls)
                .filter_by(token=token)
                .delete(synchronize_session=False))

    @classmethod
    def by_token(cls, token, session):
        """ Get the connection with the given token """
        return session.query(cls).filter_by(token=token).first()

    @classmethod
    def create(cls, session, **kwargs):
        """ Create a new connection object """

        connection = cls(**kwargs)
        session.add(connection)
        session.commit()
        return connection

    @property
    def active_users(self):
        """
            Return the list of connected user's object which are still online.
        """

        return [user for user in self.users if user.online]

    def level(self, room_id=None):
        """
            The maximum level of the users in this connection

            :param room_id: The ID of the room.
            :type room_id: int
            :return: Level of the user
            :rtype: int
        """

        if not self.active_users:
            return 0

        return max(user.level(room_id) for user in self.active_users)

    def can(self, action, room_id=None):
        """
            Return True if this connection can do the specified action

            :param action: The action to do
            :param room_id: The ID of the room where the action take place.
            :type action: smserver.ability.Permissions
            :type room_id: int
            :return: True if the action in authorized
        """

        return ability.Ability.can(action, self.level(room_id))
