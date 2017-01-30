#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from smserver.models import schema

__all__ = ['Simfile']

class Simfile(schema.Base):
    __tablename__ = 'simfiles'

    id           = Column(Integer, primary_key=True)
    song_id     = Column(Integer, ForeignKey('songs.id'))
    song = relationship("Song", back_populates="simfile")
    file_hash        = Column(String(42))

    song_stats = relationship("SongStat", back_populates="simfile")

    chart = relationship("Chart", back_populates="simfile")

    def __repr__(self):
        return "<Simfile #%s (file hash='%s')>" % (self.id, self.file_hash)

    @classmethod
    def find_or_create(cls, song_id, file_hash, session):
        simfile = session.query(cls).filter_by(song_id=song_id, file_hash=file_hash).first()
        if not simfile:
            simfile = cls(song_id=song_id, file_hash=file_hash)
            session.add(simfile)
            session.commit()

        return simfile
