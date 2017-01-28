
import enum

from sqlalchemy import Column, Integer, String, Float

from smserver.models import schema

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

    id         = Column(Integer, primary_key=True)
    chartkey   = Column(String(42))
    taps       = Column(Integer)
    jumps      = Column(Integer)
    hands      = Column(Integer)
    diff       = Column(Integer)
    rating     = Column(Float)

    def __repr__(self):
        return "<RankedChart #%s (hash='%s')>" % (self.id, self.hash)

