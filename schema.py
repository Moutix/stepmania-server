from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    password = Column(String(255))

    def __repr__(self):
        return "<User #%s (name='%s')>" % (self.id, self.name)
