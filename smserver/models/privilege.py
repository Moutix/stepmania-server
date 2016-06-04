#!/usr/bin/env python3
# -*- coding: utf8 -*-


import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from smserver.models import schema

class Privilege(schema.Base):
    __tablename__ = 'privileges'

    id         = Column(Integer, primary_key=True)

    level      = Column(Integer, default=1)

    user_id    = Column(Integer, ForeignKey('users.id'))
    user       = relationship("User", back_populates="privileges")

    room_id    = Column(Integer, ForeignKey('rooms.id'))
    room       = relationship("Room", back_populates="privileges")

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<Privileges #%s (level='%s')>" % (self.id, self.level)

    @classmethod
    def find(cls, room_id, user_id, session):
        return session.query(cls).filter_by(room_id=room_id, user_id=user_id).first()

    @classmethod
    def find_or_update(cls, room_id, user_id, session, level=1):
        priv = cls.find(room_id, user_id, session)
        if not priv:
            priv = cls(user_id=user_id, room_id=room_id)
            session.add(priv)

        priv.level = level
        session.commit()
        return priv

