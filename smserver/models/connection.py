""" Connection models """

import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from smserver.models import schema

__all__ = ['Connection']

class Connection(schema.Base):
    """ Connection Model, it representes a true connection on the server
    The data associated with the connection are store locally for performance issue.
    """

    __tablename__ = 'connections'

    id          = Column(Integer, primary_key=True)
    token       = Column(String(255), index=True)

    ip          = Column(String(255))
    port        = Column(Integer)

    users       = relationship("User", back_populates="connection")

    room_id     = Column(Integer, ForeignKey('rooms.id'))
    room        = relationship("Room", back_populates="connections")

    created_at  = Column(DateTime, default=datetime.datetime.now)
    updated_at  = Column(DateTime, onupdate=datetime.datetime.now)
    close_at    = Column(DateTime)

    def __repr__(self):
        return "<Connection #%s (ip='%s', port='%s')>" % (
            self.id, self.ip, self.port)

    @property
    def alive(self):
        """ Return true if the connection is still active """
        return bool(self.close_at)

    @classmethod
    def remove(cls, token, session):
        """ Remove the connection """

        return (session
                .query(cls)
                .filter_by(token=token)
                .delete(synchronize_session=False))
