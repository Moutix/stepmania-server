#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from sqlalchemy import Column, Integer, ForeignKey

from smserver.models import schema

__all__ = ['PackSimfiles']

class PackSimfile(schema.Base):
    __tablename__ = 'packsimfiles'

    id           = Column(Integer, primary_key=True)
    pack_id          = Column(Integer, ForeignKey("packs.id"))
    simfile_id          = Column(Integer, ForeignKey("songs.id"))


    def __repr__(self):
        return "<PackSong #%s (pack_id='%s', song_id='%s')>" % (self.id, self.pack_id, self.song_id)

    @classmethod
    def find_or_create(cls, pack_id, song_id, session):
        packsong = session.query(cls).filter_by(pack_id=pack_id, song_id=song_id).first()
        if not pack:
            packsong = cls(pack_id=pack_id, song_id=song_id)
            session.add(packsong)
            session.commit()

        return packsong
