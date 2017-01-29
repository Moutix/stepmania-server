#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, LargeBinary

from sqlalchemy.orm import relationship, object_session

from smserver.models import schema
from smserver.chathelper import with_color, nick_color
from smserver.smutils.smpacket import SMPacket, SMPayloadType

__all__ = ['SongStat']

class SongStat(schema.Base):
    __tablename__ = 'song_stats'

    GRADES = {
        0: "AAAA",
        1: "AAA",
        2: "AA",
        3: "A",
        4: "B",
        5: "C",
        6: "D",
        7: "F",
    }

    DIFFICULTIES = {
        0: "BEGINNER",
        1: "EASY",
        2: "MEDIUM",
        3: "HARD",
        4: "EXPERT",
    }

    stepid = {
        1: "hit_mine",
        2: "avoid_mine",
        3: "miss",
        4: "bad",
        5: "good",
        6: "great",
        7: "perfect",
        8: "flawless",
        9: "not_held",
        10: "held"
    }

    id         = Column(Integer, primary_key=True)

    song_id    = Column(Integer, ForeignKey('songs.id'))
    song       = relationship("Song", back_populates="stats")

    user_id    = Column(Integer, ForeignKey('users.id'))
    user       = relationship("User", back_populates="song_stats")

    game_id    = Column(Integer, ForeignKey('games.id'))
    game       = relationship("Game", back_populates="song_stats")

    hit_mine   = Column(Integer, default=0)
    avoid_mine = Column(Integer, default=0)
    miss       = Column(Integer, default=0)
    bad        = Column(Integer, default=0)
    good       = Column(Integer, default=0)
    great      = Column(Integer, default=0)
    perfect    = Column(Integer, default=0)
    flawless   = Column(Integer, default=0)
    not_held   = Column(Integer, default=0)
    held       = Column(Integer, default=0)

    max_combo  = Column(Integer, default=0)
    options    = Column(Text, default="")
    score      = Column(Integer, default=0)
    rate      = Column(Integer, default=0)

    chart_id      = Column(Integer, ForeignKey('charts.id'))
    simfile_id    = Column(Integer, ForeignKey('simfiles.id'))

    migsp      = Column(Integer, default=0)
    toasty      = Column(Integer, default=0)
    grade      = Column(Integer, default=0)
    difficulty = Column(Integer, default=0)
    feet       = Column(Integer, default=0)

    ssr = Column(Float(precision=5))
    migs = Column(Float(precision=5))

    duration   = Column(Integer, default=0)

    raw_stats  = Column(LargeBinary)

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<SongStat #%s score=%s (%s%%)>" % (self.id, self.migsp, self.migs)

    @property
    def lit_difficulty(self):
        if self.difficulty is None:
            return "Unknown"

        return self.DIFFICULTIES.get(self.difficulty, str(self.difficulty))

    @property
    def full_difficulty(self):
        return "%s (%s)" % (self.lit_difficulty, self.feet)

    @property
    def lit_grade(self):
        if self.grade is None:
            return "Unknown"

        return self.GRADES.get(self.grade, self.grade)

    def pretty_result(self, room_id=None, color=False, date=True, toasty=True, points=True, userfirst=False):
        color_func = with_color if color else lambda x, *_: x

        return ("{user_name}: {difficulty} {grade} {percentage:12.2f}% {toasty}{date}{points}" if userfirst else
             "{difficulty}: {user_name} {grade} {percentage:12.2f}% {toasty}{date}{points}").format(
            difficulty=color_func(self.full_difficulty, color=nick_color(self.lit_difficulty)),
            user_name=self.user.fullname_colored(room_id) if color else self.user.fullname(room_id),
            grade=color_func(self.lit_grade),
            percentage=self.migs,
            toasty=" Toasty:" + str(self.toasty) + " " if toasty and self.toasty > 0 else "",
            date=" on " + self.created_at.strftime("%x") if date else "",
            points=" Points: " + str(self.migsp) if points else ""
        )


    def calc_percentage(self, config=None):
        if not config:
            config = {
                "not_held": 0,
                "miss": 0,
                "bad": 0,
                "good": 0,
                "held": 3,
                "hit_mine": -2,
                "great": 1,
                "perfect": 2,
                "flawless": 3
            }

        max_weight = max(config.values())
        percentage = 0
        nb_note = 0
        for note, weight in config.items():
            nb = getattr(self, note, 0)
            percentage += nb*weight
            nb_note += nb*max_weight

        return round(percentage/nb_note*100, 2) if nb_note > 0 else 0

    def calc_xp(self, config=None, extranotes=None):
        if not config:
            config = {
                "miss": 0,
                "bad": 1,
                "good": 2,
                "great": 3,
                "perfect": 4,
                "flawless": 5,
                "toasty": 100
            }

        xp = 0
        for note, weight in config.items():
            nb = getattr(self, note, 0)
            xp += nb*weight
        for note in extranotes:
            xp+= note["size"]*config[stepid[note["stepid"]]]
        return xp


    @staticmethod
    def encode_stats(raw_data):
        binary = BinaryStats(nb_notes=len(raw_data), stats=[])

        for stats in raw_data:
            binary["stats"].append({
                "grade": stats["grade"],
                "stepid": stats["stepid"],
                "score": stats["score"],
                "combo": stats["combo"],
                "health": stats["health"],
                "time": stats["time"].seconds
            })

        return binary.payload

    @staticmethod
    def decode_stats(binary):
        return BinaryStats.from_payload(binary)["stats"]

    @property
    def stats(self):
        return self.decode_stats(self.raw_stats)

    @property
    def nb_notes(self):
        return sum(getattr(self, note, 0) for note in self.stepid.values())

    @property
    def taps(self):
        return self.miss+self.flawless+self.bad+self.good+self.perfect+self.great

    def get_rank(self, user_id, song_id):
        tbquery = (object_session(self).query(SongStat.id)
            .filter_by(chart_id = self.chart_id)
            .filter_by(feet = self.feet)
            .filter_by(song_id = self.song_id)
            .filter_by(difficulty = self.difficulty))
        pbquery = (object_session(self).query(SongStat.id)
            .filter_by(chart_id = self.chart_id)
            .filter_by(feet = self.feet)
            .filter_by(user_id = self.user_id)
            .filter_by(song_id = self.song_id)
            .filter_by(difficulty = self.difficulty))
        tb_total = tbquery.count()
        pb_total = pbquery.count()
        tb = str(tb_total - tbquery.filter(SongStat.migsp < self.migsp).count())
        pb = str(pb_total - pbquery.filter(SongStat.migsp < self.migsp).count())
        # These are probably better but using the above existing scores are placed higher
        # tb = str(tbquery.filter(SongStat.migsp < self.migsp).count() + 1)
        # pb = str(pbquery.filter(SongStat.migsp < self.migsp).count() + 1)
        tb_total = str(tb_total)
        pb_total = str(pb_total)
        return (" PB: " + with_color(pb + "/" + pb_total, "aaaa00") + " TB: " + with_color(tb + "/" + tb_total, "aaaa00"))

    @staticmethod
    def calc_grade(score, data):
        if score >= 100.00:
            for note in data:
                if note["stepid"] > 2 and note["stepid"] < 9:
                    if note != 8:
                        return 1
            return 0
        elif score >= 93.00:
            return 2
        elif score >= 80.00:
            return 3
        elif score >= 65.00:
            return 4
        elif score >= 45.00:
            return 5
        return 6

    @staticmethod
    def calc_dp(stepsid):
        if stepsid == 8 or stepsid == 7:
            return 2
        elif stepsid == 6:
            return 1
        elif stepsid == 5:
            return 0
        elif stepsid == 4:
            return -4
        elif stepsid == 3:
            return -8
        elif stepsid == 10:
            return 0
        else:
            return 0

    @staticmethod
    def calc_migsp(stepsid):
        if stepsid == 8:
            return 3
        elif stepsid == 7:
            return 2
        elif stepsid == 6:
            return 1
        elif stepsid == 5:
            return 0
        elif stepsid == 4:
            return -4
        elif stepsid == 3:
            return -8
        elif stepsid == 10:
            return 6
        else:
            return 0

    @staticmethod
    def calc_wifep(offset):
        avedeviation = 95.0
        maxms = offset*1000.0
        y = 1.0 - float(pow(2, (-1) * maxms*maxms / 9025.0))
        y = pow(y, 2)
        return (2 + 8)*(1 - y) - 8

    @staticmethod
    def calc_grade_from_ratio(score, data):
        if score >= 1:
            for note in data:
                if note["stepid"] > 2 and note["stepid"] < 9:
                    if note != 8:
                        return 1
            return 0
        elif score >= 0.93:
            return 2
        elif score >= 0.80:
            return 3
        elif score >= 0.65:
            return 4
        elif score >= 0.45:
            return 5
        return 6

    @staticmethod
    def get_stepid(offset):
        smarv  = 0.02259;
        sperf  = 0.04509;
        sgreat = 0.09009;
        sgood  = 0.13509;
        sboo   = 0.18909;
        if (offset < smarv) and (offset > (smarv * -1.0)):
            return 8
        elif (offset < sperf) and (offset > (sperf * -1.0)):
            return 7
        elif (offset < sgreat) and (offset > (sgreat * -1.0)):
            return 6
        elif (offset < sgood) and (offset > (sgood * -1.0)):
            return 5
        else:
            return 4


class BinaryStats(SMPacket):
    _payload = [
        (SMPayloadType.INT, "nb_notes", 8),
        (SMPayloadType.LIST, "stats", ("nb_notes", [
            (SMPayloadType.MSN, "grade", None),
            (SMPayloadType.LSN, "stepid", None),
            (SMPayloadType.INT, "score", 4),
            (SMPayloadType.INT, "combo", 2),
            (SMPayloadType.INT, "health", 2),
            (SMPayloadType.INT, "time", 4)
            ])
        )
    ]

