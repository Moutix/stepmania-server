

import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func, Float
from sqlalchemy.orm import relationship, reconstructor, object_session

from smserver.models import schema
from smserver.chathelper import with_color, nick_color
from smserver.models.privilege import Privilege
from smserver import ability

__all__ = ['RankedChart', 'Diffs']

class Diffs(enum.Enum):
    Beginner       = 0
    Easy       = 1
    Medium       = 2
    Hard  = 3
    Challenge      = 4
    Edit      = 5

class RankedChart(schema.Base):
    __tablename__ = 'ranked_charts'

    id                = Column(Integer, primary_key=True)
    chartkey               = Column(String(255))
    taps              = Column(Integer)
    diff          = Column(Integer)
    rating = Column(Float)
    #for skillset in Skillsets:
    #    exec(skillset.name + " = Column(Float)")

    def __repr__(self):
        return "<RankedChart #%s (hash='%s')>" % (self.id, self.hash)

