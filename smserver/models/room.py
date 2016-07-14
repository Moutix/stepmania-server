#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime
import hashlib

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy import func, or_, and_, desc
from sqlalchemy.orm import reconstructor, relationship, object_session

from smserver.smutils import smpacket
from smserver.models import schema, game, user, privilege

__all__ = ['Room']

class Room(schema.Base):
    __tablename__ = 'rooms'

    id             = Column(Integer, primary_key=True)
    name           = Column(String(255))
    motd           = Column(String(255))
    password       = Column(String(255))
    description    = Column(Text, default="")
    static         = Column(Boolean, default=False)
    ingame         = Column(Boolean, default=False)
    hidden         = Column(Boolean, default=False)

    mode           = Column(String(255))

    status         = Column(Integer, default=0)
    type           = Column(Integer, default=1)
    max_users      = Column(Integer, default=255)

    users          = relationship("User", back_populates="room")
    games          = relationship("Game", back_populates="room")
    privileges     = relationship("Privilege", back_populates="room")
    bans           = relationship("Ban", back_populates="room")

    active_song_id = Column(Integer, ForeignKey('songs.id', ondelete="SET NULL"))
    active_song    = relationship("Song", back_populates="active_rooms")

    created_at     = Column(DateTime, default=datetime.datetime.now)
    updated_at     = Column(DateTime, onupdate=datetime.datetime.now)

    @reconstructor
    def _init_on_load(self):
        self._nb_players = None

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
    def last_game(self):
        return (object_session(self)
                .query(game.Game)
                .filter_by(room_id=self.id)
                .order_by(desc(game.Game.created_at))
                .first())

    @property
    def nb_players(self):
        if self._nb_players:
            return self._nb_players

        self._nb_players = (
            object_session(self)
            .query(func.count(user.User.id))
            .filter_by(online=True, room_id=self.id)
            .scalar())

        return self._nb_players

    @property
    def online_users(self):
        return (object_session(self)
                .query(user.User)
                .filter_by(online=True, room_id=self.id)
                .all())

    @property
    def room_info(self):
        packet = smpacket.SMOPacketServerRoomInfo(
            max_players=self.max_users
        )

        song = self.active_song
        if song:
            packet["song_title"] = song.title
            packet["song_subtitle"] = song.subtitle
            packet["song_artist"] = song.artist

        packet["players"] = [user.name for user in self.online_users]
        packet["num_players"] = len(packet["players"])

        return smpacket.SMPacketServerNSSMONL(packet=packet)

    @property
    def nsccuul(self):
        """ Return the NSCCUUL packets listing users in the room """

        users = self.online_users

        return smpacket.SMPacketServerNSCCUUL(
            max_players=self.max_users,
            nb_players=len(users),
            players=[{"status": u.enum_status.value, "name": u.name}
                     for u in users]
            )

    @staticmethod
    def list_to_smopacket(rooms):
        """ Take a list of rooms and return the formatted SMO packet"""

        packet = smpacket.SMOPacketServerRoomUpdate(
            type=1,
            nb_rooms=0,
            rooms=[],
            room_status=[],
            room_flags=[]
        )

        for room in rooms:
            packet["nb_rooms"] += 1
            packet["rooms"].append({
                "title": room.name,
                "description": room.description
            })
            packet['room_status'].append(room.status)
            packet['room_flags'].append(1 if room.password else 0)

        return smpacket.SMPacketServerNSSMONL(packet=packet)

    @classmethod
    def smo_list(cls, session, users=None, min_level=2):
        """
            Return the list of rooms already formatted in a SMO packet

            Send the list of room with:

            ```serv.send(models.Room.smo_list(session))```
        """

        return cls.list_to_smopacket(cls.available_rooms(session, users, min_level))

    @classmethod
    def available_rooms(cls, session, users=None, min_level=2):
        """
            Get the available rooms for the given user(s).

            If no users provided, return all the rooms
        """

        if not users:
            return session.query(cls)

        if not isinstance(users, list):
            users = [users]

        if max(users, key=lambda u: u.rank).rank >= min_level:
            return session.query(cls)

        query_privileges = []
        for usr in users:
            query_privileges.append(
                and_(
                    privilege.Privilege.user_id == usr.id,
                    privilege.Privilege.level >= min_level
                )
            )

        return (session
                .query(cls)
                .join(privilege.Privilege)
                .filter(or_(
                    cls.hidden == False,
                    and_(
                        cls.hidden == True,
                        or_(*query_privileges)
                    )
                )))

    @classmethod
    def login(cls, name, password, session):
        """
            Find a room matching the couple name and password

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
    def reset_room_status(cls, session):
        session.query(cls).update({"status": 0})
        session.commit()

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
            room.motd = hroom.get("motd")

            max_users = hroom.get("max_users", 255)
            room.max_users = max_users if max_users > 0 and max_users < 255 else 255

            if hroom.get("password"):
                room.password = hashlib.sha256(hroom["password"].encode('utf-8')).hexdigest()

            room.static = True

            rooms.append(room)

        return rooms
