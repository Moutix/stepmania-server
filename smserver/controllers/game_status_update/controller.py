#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from smserver.smutils import smpacket

from smserver.stepmania_controller import StepmaniaController

class GameStatusUpdateController(StepmaniaController):
    command = smpacket.SMClientCommand.NSCGSU
    require_login = False

    def handle(self):
        if not self.room:
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
            self.conn.songstats[self.packet["player_id"]]["data"].append(stats)

