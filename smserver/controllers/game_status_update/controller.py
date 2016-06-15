#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from smserver import models
from smserver.smutils import smpacket
from smserver.stepmania_controller import StepmaniaController
from smserver.chathelper import with_color

class GameStatusUpdateController(StepmaniaController):
    command = smpacket.SMClientCommand.NSCGSU
    require_login = False

    def handle(self):
        if not self.conn.room:
            return

        if "start_at" not in self.conn.songstats:
            return

        stats = {"time": datetime.datetime.now() - self.conn.songstats.get("start_at"),
                 "stepid": self.packet["step_id"],
                 "grade": self.packet["grade"],
                 "score": self.packet["score"],
                 "combo": self.packet["combo"],
                 "health": self.packet["health"],
                 "offset": self.packet["offset"]
                }

        with self.conn.mutex:
            best_score = self.conn.songstats[self.packet["player_id"]]["best_score"]

        if best_score and stats["score"] > best_score:
            with self.conn.mutex:
                self.conn.songstats[self.packet["player_id"]]["best_score"] = None
            self.beat_best_score()

        with self.conn.mutex:
            self.conn.songstats[self.packet["player_id"]]["data"].append(stats)

    def beat_best_score(self):
        user = [user for user in self.users if user.pos == self.packet["player_id"]][0]

        with self.conn.mutex:
            message = "%s just beat the best score on %s(%s)" % (
                user.name,
                models.SongStat.DIFFICULTIES.get(self.conn.songstats[self.packet["player_id"]]["difficulty"]),
                self.conn.songstats[self.packet["player_id"]]["feet"]
            )

        self.sendroom(self.conn.room, smpacket.SMPacketServerNSCSU(message=message))

