#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy import select, func, desc
from sqlalchemy.orm import relationship, column_property, object_session

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
    games        = relationship("Game", back_populates="song")

    time_played  = column_property(
        select([func.count(song_stat.SongStat.id)]).\
        where(song_stat.SongStat.song_id == id).\
        correlate_except(song_stat.SongStat)
    )

    created_at   = Column(DateTime, default=datetime.datetime.now)
    updated_at   = Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<Song #%s (name='%s')>" % (self.id, self.fullname)

    @property
    def best_scores(self):
        return [self.best_score(feet[0]) for feet in
                (object_session(self)
                 .query(song_stat.SongStat.feet)
                 .filter_by(song_id=self.id)
                 .group_by(song_stat.SongStat.feet))]

    def best_score(self, feet):
        """ Return the song_stat element with the highest score for this feet """

        return (object_session(self)
                .query(song_stat.SongStat)
                .filter_by(feet=feet)
                .filter_by(song_id=self.id)
                .order_by(desc(song_stat.SongStat.score))
                .first())

    def best_score_value(self, feet):
        """ Return the highest score for this feet """

        stat = self.best_score(feet)
        if not stat:
            return None

        return stat.score

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

