

import datetime
import enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func, Float
from sqlalchemy.orm import relationship, reconstructor, object_session

from smserver.models import schema
from smserver.chathelper import with_color, nick_color
from smserver.models.privilege import Privilege
from smserver import ability

__all__ = ['Skillsets', 'RankedSong', 'Diffs']

class Skillsets(enum.Enum):
    overall       = 0
    stream       = 1
    jumpstream       = 2
    handstream  = 3
    stamina      = 4
    jackspeed       = 5
    jackstamina       = 6
    technical  = 7
    
class Diffs(enum.Enum):
    Beginner       = 0
    Easy       = 1
    Medium       = 2
    Hard  = 3
    Challenge      = 4
    Edit      = 5

class RankedSong(schema.Base):
    __tablename__ = 'ranked_songs'

    id                = Column(Integer, primary_key=True)
    chartkey               = Column(String(255))
    taps              = Column(Integer)
    diff          = Column(Integer)
    for skillset in Skillsets:
        exec(skillset.name + " = Column(Float)")
    def __repr__(self):
        return "<RankedSong #%s (hash='%s')>" % (self.id, self.hash)

