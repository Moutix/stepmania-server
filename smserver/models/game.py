#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, desc
from sqlalchemy.orm import relationship, object_session

from smserver.models import schema, song_stat, user
from smserver.smutils import smpacket

__all__ = ['Game']

class Game(schema.Base):
    __tablename__ = 'games'

    id         = Column(Integer, primary_key=True)

    active     = Column(Boolean, default=True)

    song_stats = relationship("SongStat", back_populates="game")

    song_id    = Column(Integer, ForeignKey('songs.id', ondelete="SET NULL"))
    song       = relationship("Song", back_populates="games")

    room_id    = Column(Integer, ForeignKey('rooms.id', ondelete="SET NULL"))
    room       = relationship("Room", back_populates="games")

    end_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<Game #%s)>" % (self.id)

    @property
    def scoreboard_packet(self):
        packet = smpacket.SMPacketServerNSCGON(
            nb_players=0,
            ids=[]
        )

        session = object_session(self)


        options = ("score", "grade", "difficulty", "miss", "bad",
                   "good", "great", "perfect", "flawless", "held",
                   "max_combo", "options")

        for option in options:
            packet[option] = []

        for songstat in (session.query(song_stat.SongStat)
                         .filter_by(game_id=self.id)
                         .order_by(desc(song_stat.SongStat.score))):

            packet["nb_players"] += 1
            packet["ids"].append(user.User.user_index(songstat.user.id, self.room_id, session))
            for option in options:
                packet[option].append(getattr(songstat, option, None))

        return packet

