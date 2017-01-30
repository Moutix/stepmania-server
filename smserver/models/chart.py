#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from smserver.models import schema

__all__ = ['Chart']

class Chart(schema.Base):
    __tablename__ = 'charts'

    id           = Column(Integer, primary_key=True)
    chartkey        = Column(String(42))

    song_stats = relationship("SongStat", back_populates="chart")

    simfile_id = Column(Integer, ForeignKey('simfiles.id'))
    simfile = relationship("Simfile", back_populates="chart")

    def __repr__(self):
        return "<Chart #%s (chartkey='%s')>" % (self.id, self.chartkey)

    @classmethod
    def find_or_create(cls, chartkey, simfile_id, session):
        chart = session.query(cls).filter_by(chartkey=chartkey, simfile_id=simfile_id).first()
        if not chart:
            chart = cls(chartkey=chartkey, simfile_id=simfile_id)
            session.add(chart)
            session.commit()

        return chart

