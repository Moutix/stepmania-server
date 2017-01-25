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
            pid = self.packet["player_id"]
            best_score = self.conn.songstats[pid]["best_score"]

        if best_score and self.conn.songstats[pid]["dpacum"] > best_score:
            with self.conn.mutex:
                self.conn.songstats[self.packet["player_id"]]["best_score"] = None
            self.beat_best_score()

        with self.conn.mutex:
            offset = float(stats["offset"]) / 2000.0 - 16.384
            if stats["stepid"] > 3 and stats["stepid"] < 9:
                stats["stepid"] = self.get_stepid(offset)
                self.conn.songstats[pid]["taps"] += 1
            if stats["stepid"] > 3 and stats["stepid"] < 6:
                stats["combo"] = 0
                self.conn.songstats[pid]["perfect_combo"] = 0
            elif stats["stepid"] > 6 and stats["stepid"] < 9:
                if len(self.conn.songstats[pid]["data"]) > 1:
                    stats["combo"] = self.conn.songstats[pid]["data"][-1]["combo"] + 1
                    self.conn.songstats[pid]["perfect_combo"] += 1
            elif stats["stepid"] == 5:
                if len(self.conn.songstats[pid]["data"]) > 1:
                    stats["combo"] = self.conn.songstats[pid]["data"][-1]["combo"] + 1
                    self.conn.songstats[pid]["perfect_combo"] = 0
            elif stats["stepid"] == 10 or stats["stepid"] == 9:
                self.conn.songstats[pid]["holds"] += 1
                if len(self.conn.songstats[pid]["data"]) > 1:
                    stats["combo"] = self.conn.songstats[pid]["data"][-1]["combo"]
            elif stats["stepid"] == 3 :
                self.conn.songstats[pid]["taps"] += 1
                stats["combo"] = 0
                self.conn.songstats[pid]["perfect_combo"] = 0
            self.conn.songstats[pid]["data"].append(stats)
            self.conn.songstats[pid]["offsetacum"] += offset
            self.conn.songstats[pid]["dpacum"] += self.dp(stats["stepid"])
            if self.conn.songstats[pid]["perfect_combo"] % 250:
                self.conn.songstats[pid]["toasties"] += 1

    def beat_best_score(self):
        user = [user for user in self.users if user.pos == self.packet["player_id"]][0]

        with self.conn.mutex:
            message = "%s just beat the best score on %s(%s)" % (
                user.name,
                models.SongStat.DIFFICULTIES.get(self.conn.songstats[self.packet["player_id"]]["difficulty"]),
                self.conn.songstats[self.packet["player_id"]]["feet"]
            )

        self.sendroom(self.conn.room, smpacket.SMPacketServerNSCSU(message=message))


    def get_stepid(self, offset):
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


    def dp(self, stepsid):
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
            return 6
        else:
            return 0