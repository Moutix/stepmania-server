#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime
import hashlib

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, or_, and_, Boolean
from sqlalchemy.orm import relationship

from smutils import smpacket
import models.schema

class Room(models.schema.Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    password = Column(String(255))
    description = Column(Text, default="")
    static = Column(Boolean, default=False)

    status = Column(Integer, default=0)
    type = Column(Integer, default=1)
    users = relationship("User", back_populates="room")

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<Room #%s (name='%s')>" % (self.id, self.name)

    def to_packet(self):
        return smpacket.SMOPacketServerRoomUpdate(
            type=0,
            room_title=self.name,
            room_description=self.description,
            room_type=self.type
        )

    @staticmethod
    def list_smopacket(rooms):
        packet = smpacket.SMOPacketServerRoomUpdate(
            type=1,
            nb_rooms=len(rooms),
            rooms=[],
            room_status=[],
            room_flags=[]
        )

        for room in rooms:
            packet["rooms"].append({
                "title": room.name,
                "description": room.description
            })
            packet['room_status'].append(room.status)
            packet['room_flags'].append(1 if room.password else 0)

        return smpacket.SMPacketServerNSSMONL(packet=packet)

    @classmethod
    def smo_list(cls, session):
        rooms = session.query(Room).all()
        return cls.list_smopacket(rooms)

    @classmethod
    def login(cls, name, password, session):
        return (
            session.query(cls)
            .filter_by(name=name)
            .filter(or_(
                cls.password.is_(None),
                and_(
                    cls.password.isnot(None),
                    cls.password == hashlib.sha256(password.encode('utf-8')).hexdigest()
                )))
            .first()
            )

    @classmethod
    def init_from_hashes(cls, hrooms, session):
        rooms = []

        for hroom in hrooms:
            room = session.query(cls).filter_by(name=hroom["name"]).first()

            if not room:
                room = cls(name=hroom["name"])
                session.add(room)

            room.description = hroom.get("description", "")
            if hroom.get("password"):
                room.password = hashlib.sha256(hroom["password"].encode('utf-8')).hexdigest()
            room.static = True

            rooms.append(room)

        return rooms


