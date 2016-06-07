#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from smserver.models import schema

__all__ = ['Song']

class BanIP(schema.Base):
    __tablename__ = 'ban_ips'

    id         = Column(Integer, primary_key=True)
    ip         = Column(String(255))
    time       = Column(Integer)
    fixed      = Column(Boolean, default=False)

    room_id    = Column(Integer, ForeignKey('rooms.id'))
    room       = relationship("Room", back_populates="ban_ips")

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<BanIP #%s (ip='%s')>" % (self.id, self.ip)

    @classmethod
    def ban(cls, session, ip, time=None, room_id=None, fixed=False):
        """ Add an IP to the ban list """

        if cls.is_ban(session, ip, room_id):
            return None

        ban_ip = cls(ip=ip, time=time, room_id=room_id, fixed=fixed)
        session.add(ban_ip)

        session.commit()
        return ban_ip

    @classmethod
    def is_ban(cls, session, ip, room_id=None):
        """ Check if an IP is on the ban list """

        ban_ip = session.query(cls).filter_by(ip=ip, room_id=room_id).first()
        return bool(ban_ip)

    @classmethod
    def unban(cls, session, ip, room_id=None, fixed=False):
        """ Unban an IP. Return True on success"""

        ban_ip = session.query(cls).filter_by(ip=ip, room_id=room_id, fixed=fixed).first()
        if not ban_ip:
            return False

        session.delete(ban_ip)
        session.commit()
        return True

    @classmethod
    def reset_ban(cls, session, room_id=None, fixed=False):
        """ Delete all the IP from the ban list for the given room """

        return session.query(cls).filter_by(room_id=room_id, fixed=fixed).delete()

