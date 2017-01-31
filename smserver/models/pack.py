#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from smserver.models import schema

__all__ = ['Pack']

class Pack(schema.Base):
    __tablename__ = 'packs'

    id           = Column(Integer, primary_key=True)
    name        = Column(String(128))
    abr        = Column(String(16))

    ranked_charts = relationship("RankedChart", back_populates="pack")

    def __repr__(self):
        return "<Pack #%s (name='%s')>" % (self.id, self.name)

    @classmethod
    def find_or_create(cls, name, session):
        pack = session.query(cls).filter_by(name=name).first()
        if not pack:
            pack = cls(name=name)
            session.add(pack)
            session.commit()

        return pack

