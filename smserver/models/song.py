#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy import select, func
from sqlalchemy.orm import relationship, column_property

from smserver.models import schema, song_stat

__all__ = ['Song']

class Song(schema.Base):
    __tablename__ = 'songs'

    id           = Column(Integer, primary_key=True)
    title        = Column(String(255))
    subtitle     = Column(String(255))
    artist       = Column(Text, default="")

    active_rooms = relationship("Room", back_populates="active_song")

    stats        = relationship("SongStat", back_populates="song")

    time_played  = column_property(
            select([func.count(song_stat.SongStat.id)]).\
            where(song_stat.SongStat.song_id==id).\
            correlate_except(song_stat.SongStat)
        )

    created_at   = Column(DateTime, default=datetime.datetime.now)
    updated_at   = Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<Song #%s (name='%s')>" % (self.id, self.fullname)



    @property
    def fullname(self):
        return "%s (%s)" % (self.title, self.artist)

    @classmethod
    def find_or_create(cls, title, subtitle, artist, session):
        song = session.query(cls).filter_by(title=title, artist=artist, subtitle=subtitle).first()
        if not song:
            song = cls(title=title, artist=artist, subtitle=subtitle)
            session.add(song)
            session.commit()

        return song

