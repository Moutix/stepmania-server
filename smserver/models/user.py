#!/usr/bin/env python3
# -*- coding: utf8 -*-


import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from smserver.smutils import smpacket
from smserver.models import schema
from smserver.models.privilege import Privilege
from smserver import ability

__all__ = ['UserStatus', 'User']

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

    created_at        = Column(DateTime, default=datetime.datetime.now)
    updated_at        = Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<User #%s (name='%s')>" % (self.id, self.name)

    @property
    def enum_status(self):
        return UserStatus(self.status)

    def fullname(self, session, room_id=None):
        return "%s%s" % (
            self._level_to_symbol(self.level(session, room_id)),
            self.name)

    def can(self, action, session, room_id=None):
        return ability.Ability.can(action, self.level(session, room_id))

    def cannot(self, action, session, room_id=None):
        return ability.Ability.cannot(action, self.level(session, room_id))

    def level(self, session, room_id=None):
        if not room_id:
            return self.rank

        priv = self.room_privilege(session, room_id)
        if priv:
            return priv.level

        return 0

    def room_privilege(self, session, room_id=None):
        return Privilege.find(room_id, self.id, session)

    def set_level(self, room_id, level, session):
        if not room_id:
            self.rank = level
            session.commit()
            return level

        Privilege.find_or_update(room_id, self.id, session, level=level)
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
    def connect(cls, name, pos, session):
        user = session.query(cls).filter_by(name=name).first()
        if not user:
            user = cls(name=name)
            session.add(user)
        user.online = True
        user.pos = pos

        session.commit()

        return user

    @classmethod
    def onlines(cls, session):
        return session.query(User).filter_by(online=True).all()

    @classmethod
    def user_index(cls, user_id, session):
        for idx, user in enumerate(cls.onlines(session)):
            if user_id == user.id:
                return idx

        return 0


    @classmethod
    def sm_list(cls, session, max_users=255):
        users = cls.onlines(session)

        return smpacket.SMPacketServerNSCCUUL(
            max_players=max_users,
            nb_players=len(users),
            players=[{"status": u.enum_status.value, "name": u.name}
                     for u in users]
            )

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

