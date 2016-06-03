#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from smserver.smutils import smpacket
from smserver.stepmania_controller import StepmaniaController
from smserver import models

class GameOverController(StepmaniaController):
    command = smpacket.SMClientCommand.NSCGON
    require_login = True

    def handle(self):
        if not self.room:
            return

        song_duration = datetime.datetime.now() - self.conn.songstats["start_at"]

        for user in self.active_users:
            with self.conn.mutex:
                self.create_stats(user, self.conn.songstats[user.pos], song_duration)

        with self.conn.mutex:
            self.conn.ingame = False
            self.conn.songstats = {0: {"data": []}, 1: {"data": []}}
            self.conn.song = None

    def create_stats(self, user, raw_stats, duration):
        songstat = models.SongStat(song_id=self.conn.song, user_id=user.id)

        songstat.duration = duration.seconds

        if raw_stats["data"]:
            songstat.grade = raw_stats["data"][-1]["grade"]
            songstat.score = raw_stats["data"][-1]["score"]

        songstat.feet = raw_stats["feet"]
        songstat.difficulty = raw_stats["difficulty"]
        songstat.options = raw_stats["options"]

        songstat.max_combo = 0

        for stepid in models.SongStat.stepid.values():
            setattr(songstat, stepid, 0)

        for value in raw_stats["data"]:
            if value["combo"] > songstat.max_combo:
                songstat.max_combo = value["combo"]

            if value["stepid"] not in models.SongStat.stepid:
                continue

            setattr(songstat,
                    models.SongStat.stepid[value["stepid"]],
                    getattr(songstat, models.SongStat.stepid[value["stepid"]]) + 1
                   )

        songstat.percentage = songstat.calc_percentage()
        songstat.raw_stats = models.SongStat.encode_stats(raw_stats["data"])

        self.session.add(songstat)

        return songstat

