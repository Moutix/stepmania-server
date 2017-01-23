#!/usr/bin/env python3
# -*- coding: utf8 -*-


import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship, reconstructor, object_session

from smserver.models import schema
from smserver.chathelper import with_color, nick_color
from smserver.models.privilege import Privilege
from smserver import ability

class Friendship(schema.Base):
    __tablename__ = 'friendships'

    REPR = {
        0: "",
        2: "%",
        3: "@",
        5: "&",
        10: "~"
    }

    id                = Column(Integer, primary_key=True)
    user1_id               = Column(Integer)
    user2_id              = Column(Integer)
    state          = Column(Integer, default=0)

    def __repr__(self):
        return "<Friendship #%s (user1_id='%s', user2_id='%s')>" % (self.id, self.user1_id, self.user2_id)



