#!/usr/bin/env python3
# -*- coding: utf8 -*-


import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship, reconstructor, object_session

from smserver.models import schema
from smserver.models.privilege import Privilege
from smserver import ability

__all__ = ['UserStatus', 'User', 'AlreadyConnectError']

class AlreadyConnectError(Exception):
    pass

class UserStatus(enum.Enum):
    unknown         = 0
    room_selection  = 1
    music_selection = 2
    option          = 3
    evaluation      = 4

class User(schema.Base):
    __tablename__ = 'users'

    REPR = {
        0: "",
        2: "%",
        3: "@",
        5: "&",
        10: "~"
    }

    id                = Column(Integer, primary_key=True)
    pos               = Column(Integer)
    name              = Column(String(255))
    password          = Column(String(255))
    email             = Column(String(255))
    rank              = Column(Integer, default=1)
    xp                = Column(Integer, default=0)
    last_ip           = Column(String(255))
    stepmania_version = Column(Integer)
    stepmania_name    = Column(String(255))
    online            = Column(Boolean)
    status            = Column(Integer, default=1)

    room_id           = Column(Integer, ForeignKey('rooms.id'))
    room              = relationship("Room", back_populates="users")

    song_stats        = relationship("SongStat", back_populates="user")
    privileges        = relationship("Privilege", back_populates="user")
    bans              = relationship("Ban", back_populates="user")

    created_at        = Column(DateTime, default=datetime.datetime.now)
    updated_at        = Column(DateTime, onupdate=datetime.datetime.now)

    @reconstructor
    def _init_on_load(self):
        self._room_level = {}

    def __repr__(self):
        return "<User #%s (name='%s')>" % (self.id, self.name)

    @property
    def enum_status(self):
        return UserStatus(self.status)

    def fullname(self, room_id=None):
        return "%s%s" % (
            self._level_to_symbol(self.level(room_id)),
            self.name)

    def can(self, action, room_id=None):
        return ability.Ability.can(action, self.level(room_id))

    def cannot(self, action, room_id=None):
        return ability.Ability.cannot(action, self.level(room_id))

    def level(self, room_id=None):
        if not room_id:
            return self.rank

        priv = self.room_privilege(room_id)
        if priv:
            return priv.level

        return 0

    def room_privilege(self, room_id):
        if room_id in self._room_level:
            return self._room_level[room_id]

        priv = Privilege.find(room_id, self.id, object_session(self))

        self._room_level[room_id] = priv

        return priv

    def set_level(self, room_id, level):
        session = object_session(self)
        if not room_id:
            self.rank = level
            session.commit()
            return level

        priv = Privilege.find_or_update(room_id, self.id, session, level=level)
        self._room_level[room_id] = priv

        return level

    @classmethod
    def _level_to_symbol(cls, level):
        symbol = cls.REPR.get(level)
        if symbol:
            return symbol

        keys = sorted(cls.REPR.keys(), reverse=True)

        for key in keys:
            if key < level:
                return cls.REPR[key]

        return cls.REPR[keys[-1]]

    @classmethod
    def get_from_ids(cls, ids, session):
        """ Return a list of user instance from the ids list """

        if not ids:
            return []

        return session.query(cls).filter(cls.id.in_(ids))

    @classmethod
    def get_from_pos(cls, ids, pos, session):
        if not ids:
            return None

        return session.query(cls).filter(
            cls.id.in_(ids),
            cls.pos == pos
        ).first()

    @classmethod
    def connect(cls, name, pos, session):
        user = session.query(cls).filter_by(name=name).first()
        if not user:
            user = cls(name=name)
            session.add(user)

        if user.online:
            raise AlreadyConnectError

        user.online = True
        user.pos = pos

        session.commit()

        return user


    @classmethod
    def nb_onlines(cls, session):
        return session.query(func.count(User.id)).filter_by(online=True).scalar()

    @classmethod
    def onlines(cls, session, room_id=None):
        users = session.query(User).filter_by(online=True)
        if room_id:
            users = users.filter_by(room_id=room_id)

        return users.all()

    @classmethod
    def user_index(cls, user_id, room_id, session):
        for idx, user in enumerate(cls.onlines(session, room_id)):
            if user_id == user.id:
                return idx

        return 0

    @classmethod
    def disconnect(cls, user, session):
        user.online = False
        user.pos = None
        user.room_id = None
        session.commit()
        return user

    @classmethod
    def disconnect_all(cls, session):
        users = session.query(User).all()

        for user in users:
            user.pos = None
            user.online = False
            user.room_id = None

        session.commit()

