#!/usr/bin/env python3
# -*- coding: utf8 -*-

__all__ = ['Room']

import datetime
import hashlib

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, or_, and_, Boolean
from sqlalchemy.orm import relationship

from smserver.smutils import smpacket
from smserver.models import schema

class Room(schema.Base):
    __tablename__ = 'rooms'

    id             =  Column(Integer, primary_key=True)
    name           =  Column(String(255))
    password       =  Column(String(255))
    description    =  Column(Text, default="")
    static         =  Column(Boolean, default=False)

    status         =  Column(Integer, default=0)
    type           =  Column(Integer, default=1)
    users          =  relationship("User", back_populates="room")

    active_song_id =  Column(Integer, ForeignKey('songs.id'))
    active_song    =  relationship("Song", back_populates="active_rooms")

    created_at     =  Column(DateTime, default=datetime.datetime.now)
    updated_at     =  Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<Room #%s (name='%s')>" % (self.id, self.name)

    def to_packet(self):
        return smpacket.SMOPacketServerRoomUpdate(
            type=0,
            room_title=self.name,
            room_description=self.description,
            room_type=self.type
        )

    @property
    def room_info(self):
        packet = smpacket.SMOPacketServerRoomInfo(
            max_players=255
        )

        song = self.active_song
        if song:
            packet["song_title"] = song.title
            packet["song_subtitle"] = song.subtitle
            packet["song_artist"] = song.artist

        packet["players"] = [user.name for user in self.users]
        packet["num_players"] = len(packet["players"])

        return smpacket.SMPacketServerNSSMONL(packet=packet)

    @staticmethod
    def _list_smopacket(rooms):
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
        """ Return the list of rooms already formatted in a SMO packet
        Send the list of room with:
            serv.send(models.Room.smo_list(session))
        """

        rooms = session.query(Room).all()
        return cls._list_smopacket(rooms)

    @classmethod
    def login(cls, name, password, session):
        """ Find a room matching the couple name and password
        Return the room if the match is good
        """

        if password:
            password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        return (
            session.query(cls)
            .filter_by(name=name)
            .filter(or_(
                cls.password.is_(None),
                and_(
                    cls.password.isnot(None),
                    cls.password == password
                )))
            .first()
            )

    @classmethod
    def init_from_hashes(cls, hrooms, session):
        rooms = []

        if not hrooms:
            return rooms

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


