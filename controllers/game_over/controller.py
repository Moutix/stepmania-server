#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from smutils import smpacket

from stepmania_controller import StepmaniaController
import models

class GameOverController(StepmaniaController):
    command = smpacket.SMClientCommand.NSCGON

    def handle(self):
        if not self.room:
            return

        song_duration = datetime.datetime.now() - self.conn.songs["start_at"]

        for user in self.active_users:
            with self.conn.mutex:
                self.create_stats(user, self.conn.songs[user.pos], song_duration)

        with self.conn.mutex:
            self.conn.songs = {0: {"data": []}, 1: {"data": []}}
            self.conn.song = None

    def create_stats(self, user, raw_stats, duration):
        songstat = models.SongStat(song_id=self.conn.song, user_id=user.id)

        songstat.duration = duration.seconds
        songstat.grade = raw_stats["data"][-1]["grade"]
        songstat.score = raw_stats["data"][-1]["score"]
        songstat.feet = raw_stats["feet"]
        songstat.difficulty = raw_stats["difficulty"]
        songstat.options = raw_stats["options"]

        songstat.max_combo = 0

        for value in raw_stats["data"]:
            if value["combo"] > songstat.max_combo:
                songstat.max_combo = value["combo"]

        self.session.add(songstat)

        return songstat

