#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime
from smutils import smpacket

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    password = Column(String(255))
    email = Column(String(255))
    rank = Column(Integer, default=0)
    xp = Column(Integer, default=0)
    last_ip = Column(String(255))
    rooms = relationship("Room", back_populates="creator")

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<User #%s (name='%s')>" % (self.id, self.name)

class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    password = Column(String(255))
    description = Column(Text, default="")
    status = Column(Integer, default=0)
    type = Column(Integer, default=1)
    creator_id = Column(Integer, ForeignKey('users.id', ondelete="SET NULL"))
    creator = relationship("User", back_populates="rooms")

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
            rooms={},
            room_status=[],
            room_flags=[]
        )

        for room in rooms:
            packet["rooms"].append({
                "title": room.name,
                "description": room.description
            })
            packet['status'].append(room.status)
            packet['flags'].append(1 if room.password else 0)

        return smpacket.SMPacketServerNSSMONL(packet=packet)

    @classmethod
    def smo_list(cls, session):
        rooms = session.query(Room).all()
        return cls.list_smopacket(rooms)

