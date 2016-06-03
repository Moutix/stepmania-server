#!/usr/bin/env python3
# -*- coding: utf8 -*-

__all__ = ['SongStat']

import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, LargeBinary

from sqlalchemy.orm import relationship

from smserver.models import schema
from smserver.smutils.smpacket import SMPacket, SMPayloadType

class SongStat(schema.Base):
    __tablename__ = 'song_stats'

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

    id         =  Column(Integer, primary_key=True)

    song_id    =  Column(Integer, ForeignKey('songs.id'))
    song       =  relationship("Song", back_populates="stats")

    user_id    =  Column(Integer, ForeignKey('users.id'))
    user       =  relationship("User", back_populates="song_stats")

    hit_mine   =  Column(Integer, default=0)
    avoid_mine =  Column(Integer, default=0)
    miss       =  Column(Integer, default=0)
    bad        =  Column(Integer, default=0)
    good       =  Column(Integer, default=0)
    great      =  Column(Integer, default=0)
    perfect    =  Column(Integer, default=0)
    flawless   =  Column(Integer, default=0)
    not_held   =  Column(Integer, default=0)
    held       =  Column(Integer, default=0)

    max_combo  =  Column(Integer, default=0)
    options    =  Column(Text, default="")
    score      =  Column(Integer, default=0)
    grade      =  Column(Integer, default=0)
    difficulty =  Column(Integer, default=0)
    feet       =  Column(Integer, default=0)

    percentage =  Column(Float(precision=5))

    duration   =  Column(Integer, default=0)

    raw_stats  =  Column(LargeBinary)

    created_at =  Column(DateTime, default=datetime.datetime.now)
    updated_at =  Column(DateTime, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<SongStat #%s score=%s (%s%%)>" % (self.id, self.score, self.percentage)

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

        return percentage/nb_note*100 if nb_note > 0 else 0

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

