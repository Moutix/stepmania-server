#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy import or_
from sqlalchemy.orm import relationship

from smserver.models import schema

__all__ = ['Ban']

class Ban(schema.Base):
    __tablename__ = 'bans'

    id         = Column(Integer, primary_key=True)
    ip         = Column(String(255))
    fixed      = Column(Boolean, default=False)

    user_id    = Column(Integer, ForeignKey('users.id'))
    user       = relationship("User", back_populates="bans")

    room_id    = Column(Integer, ForeignKey('rooms.id', ondelete="SET NULL"))
    room       = relationship("Room", back_populates="bans")

    end_at     = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<Ban #%s (ip='%s', user_id='%s', room_id='%s'>" % (
            self.id, self.ip, self.user_id, self.room_id)

    @classmethod
    def ban(cls, session, ip=None, user_id=None, room_id=None, fixed=False, duration=None):
        """ Ban an IP or user from a room or the server """

        ban = cls.find_ban(session, ip, user_id, room_id)
        if not ban:
            ban = cls(user_id=user_id, room_id=room_id, ip=ip)
            session.add(ban)

        ban.end_at = datetime.datetime.now() + duration if duration else None
        if fixed:
            ban.fixed = fixed

        session.commit()
        return ban

    @classmethod
    def is_ban(cls, session, ip=None, user_id=None, room_id=None):
        """ Check if an IP or user is ban list """

        return bool(cls.find_ban(session, ip, user_id, room_id))

    @classmethod
    def find_ban(cls, session, ip=None, user_id=None, room_id=None):
        """ Check if an IP is on the ban list """
        if ip:
            ban = session.query(cls).filter_by(ip=ip, room_id=room_id)
        else:
            ban = session.query(cls).filter_by(user_id=user_id, room_id=room_id)

        return ban.filter(or_(cls.end_at.is_(None), cls.end_at > datetime.datetime.now())).first()

    @classmethod
    def unban(cls, session, ip=None, user_id=None, room_id=None):
        """ Unban an IP. Return True on success"""

        ban = cls.find_ban(session, ip, user_id, room_id)
        if not ban:
            return False

        session.delete(ban)
        session.commit()
        return True

    @classmethod
    def reset_ban(cls, session, room_id=None, fixed=False):
        """ Delete all the ban for the given room """

        return session.query(cls).filter_by(room_id=room_id, fixed=fixed).delete()

