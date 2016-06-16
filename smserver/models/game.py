#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship, column_property, object_session

from smserver.models import schema, song_stat

__all__ = ['Game']

class Game(schema.Base):
    __tablename__ = 'games'

    id         = Column(Integer, primary_key=True)

    active     = Column(Boolean, default=True)

    song_stats = relationship("SongStat", back_populates="game")

    song_id    = Column(Integer, ForeignKey('songs.id'))
    song       = relationship("Song", back_populates="games")

    room_id    = Column(Integer, ForeignKey('rooms.id'))
    room       = relationship("Room", back_populates="games")

    end_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<Game #%s)>" % (self.id)

