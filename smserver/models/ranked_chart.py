
import enum

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from smserver.models import schema
from smserver.models.song_stat import SongStat
from smserver.models.chart import Chart


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

    song_id    = Column(Integer, ForeignKey('songs.id'))
    song       = relationship("Song", back_populates="ranked_charts")

    def __repr__(self):
        return "<RankedChart #%s (hash='%s')>" % (self.id, self.hash)

    def remove(self, session):
        chart = session.query(Chart).filter_by(chartkey=self.chartkey).first()
        if chart:
            songstats = session.query(SongStat).filter_by(chart_id=chart.id).all()
            for songstat in songstats:
                songstat.ssr = 0
        session.delete(self)
        session.commit()

    @staticmethod
    def calc_ssr(rating, dppercent):
        return rating * dppercent / 93

    def update(self, updated_obj, users, session):
        self.rating = updated_obj.rating
        self.hands = updated_obj.hands
        self.jumps = updated_obj.jumps
        self.taps = updated_obj.taps
        self.diff = updated_obj.diff
        self.song_id = updated_obj.song_id
        chart = session.query(Chart).filter_by(chartkey=self.chartkey).first()
        if not users:
            users_to_recalc = []
        else:
            users_to_recalc = users
        if chart:
            songstats = session.query(SongStat).filter_by(chart_id=chart.id).all()
            for songstat in songstats:
                if songstat.ssr > 0:
                    previousssr = songstat.ssr
                    songstat.ssr = calc_ssr(chart.rating, 
                        (songstat.flawless*SongStat.calc_dp(8) + 
                        songstat.perfect*SongStat.calc_dp(7) + 
                        songstat.great*SongStat.calc_dp(6) + 
                        songstat.good*SongStat.calc_dp(5) + 
                        songstat.bad*SongStat.calc_dp(4) + 
                        songstat.miss*SongStat.calc_dp(3)) 
                        * 100 / self.taps * SongStat.calc_dp(8))
                    if previoussr != songstat.ssr and songstat.user not in users_to_recalc:
                        users_to_recalc.append(songstat.user)
        session.commit()
        return users_to_recalc