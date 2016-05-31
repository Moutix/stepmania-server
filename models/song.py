#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime
import hashlib

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, or_, and_, Boolean
from sqlalchemy.orm import relationship

from smutils import smpacket
import models.schema

class Song(models.schema.Base):
    __tablename__ = 'songs'

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    subtitle = Column(String(255))
    artist = Column(Text, default="")

    active_rooms = relationship("Room", back_populates="active_song")

    stats = relationship("SongStat", back_populates="song")

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<Song #%s (name='%s')>" % (self.id, self.title)

    @classmethod
    def find_or_create(cls, title, subtitle, artist, session):
        song = session.query(cls).filter_by(title=title, artist=artist, subtitle=subtitle).first()
        if not song:
            song = cls(title=title, artist=artist, subtitle=subtitle)
            session.add(song)
            session.commit()

        return song

