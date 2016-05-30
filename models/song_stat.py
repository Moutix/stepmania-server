#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, LargeBinary

from sqlalchemy.orm import relationship

import models.schema

class SongStat(models.schema.Base):
    __tablename__ = 'song_stats'

    id = Column(Integer, primary_key=True)

    song_id = Column(Integer, ForeignKey('songs.id'))
    song = relationship("Song", back_populates="stats")

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="song_stats")

    flawless = Column(Integer, default=0)
    perfect = Column(Integer, default=0)
    great = Column(Integer, default=0)
    good = Column(Integer, default=0)
    bad = Column(Integer, default=0)
    miss = Column(Integer, default=0)
    mine = Column(Integer, default=0)
    held = Column(Integer, default=0)
    not_held = Column(Integer, default=0)
    hit_mine = Column(Integer, default=0)
    avoid_mine = Column(Integer, default=0)

    max_combo = Column(Integer, default=0)
    options = Column(Text, default="")
    score = Column(Integer, default=0)
    grade = Column(Integer, default=0)
    difficulty = Column(Integer, default=0)
    feet = Column(Integer, default=0)

    percentage = Column(Float(precision=5))

    duration = Column(Integer, default=0)

    raw_result = Column(LargeBinary)

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<SongStat #%s>" % (self.id)

