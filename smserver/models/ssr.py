#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from sqlalchemy import Column, Integer, ForeignKey, Float, String
from sqlalchemy import select, func, desc
from smserver.models import schema, song_stat, user

__all__ = ['SSR']

class SSR(schema.Base):
    __tablename__ = 'ssrs'

    id           = Column(Integer, primary_key=True)
    song_stat_id        = Column(Integer, ForeignKey('song_stats.id'))
    user_id    = Column(Integer, ForeignKey('users.id'))
    song_id    = Column(Integer, ForeignKey('songs.id'))
    chartkey   = Column(String(255))
    skillset    = Column(Integer)
    ssr    = Column(Float)
