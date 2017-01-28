#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from sqlalchemy import Column, Integer, String, ForeignKey

from smserver.models import schema

__all__ = ['Chart']

class Chart(schema.Base):
    __tablename__ = 'charts'

    id           = Column(Integer, primary_key=True)
    simfile_id     = Column(Integer, ForeignKey('simfiles.id'))
    chartkey        = Column(String(42))

    def __repr__(self):
        return "<Chart #%s (chartkey='%s')>" % (self.id, self.chartkey)

    @classmethod
    def find_or_create(cls, simfile_id, chartkey, session):
        chart = session.query(cls).filter_by(simfile_id=simfile_id, chartkey=chartkey).first()
        if not chart:
            chart = cls(simfile_id=simfile_id, chartkey=chartkey)
            session.add(chart)
            session.commit()

        return chart

