#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

import models.schema

class UserStatus(enum.Enum):
    unknown = 1
    music_selection = 2
    option = 3
    evaluation = 4
    room_selection = 5

class User(models.schema.Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    password = Column(String(255))
    email = Column(String(255))
    rank = Column(Integer, default=0)
    xp = Column(Integer, default=0)
    last_ip = Column(String(255))
    online = Column(Boolean)
    status = Column(Integer, default=1)

    room_id = Column(Integer, ForeignKey('rooms.id'))
    room = relationship("Room", back_populates="users")

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<User #%s (name='%s')>" % (self.id, self.name)

    @property
    def enum_status(self):
        return UserStatus(self.status)

    @classmethod
    def connect(cls, name, ip, session):
        user = session.query(cls).filter_by(name=name).first()
        if not user:
            user = models.User(name=name)
            session.add(user)
        user.online = True
        user.last_ip = ip

        session.commit()

        return user

    @classmethod
    def disconnect(cls, user, session):
        user.online = False
        session.commit()
        return user

