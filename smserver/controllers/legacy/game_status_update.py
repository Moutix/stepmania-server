""" GameStatusUpdate controller module """

import datetime

from smserver import models
from smserver.smutils.smpacket import smpacket
from smserver.smutils.smpacket import smcommand
from smserver.stepmania_controller import StepmaniaController


class GameStatusUpdateController(StepmaniaController):
    command = smcommand.SMClientCommand.NSCGSU
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
                #"note_size": self.packet["note_size"], Requires smpacket update
                 "offset": self.packet["offset"]
                }

        with self.conn.mutex:
            pid = self.packet["player_id"]
            best_score = self.conn.songstats[pid]["best_score"]

            ''' requires smapcket update
            if not stats["note_size"] or stats["note_size"] <= 0:
                notesize = self.notesize_from_combo(stats["combo"], self.conn.songstats[pid]["data"])
            else:
                notesize = stats["note_size"]
            '''
            notesize = self.notesize_from_combo(stats["combo"], self.conn.songstats[pid]["data"])
            offset = float(stats["offset"]) / 2000.0 - 16.384
            if stats["stepid"] > 3 and stats["stepid"] < 9:
                self.conn.songstats[pid]["taps"] += 1
                stats["stepid"] = models.SongStat.get_stepid(offset)
                if stats["stepid"] == 7 or stats["stepid"] == 8:
                    self.conn.songstats[pid]["perfect_combo"] += notesize
                elif stats["stepid"] == 4 or stats["stepid"] == 5 or stats["stepid"] == 6:
                    self.conn.songstats[pid]["perfect_combo"] = 0
            if stats["stepid"] == 3:
                    self.conn.songstats[pid]["perfect_combo"] = 0
            if self.conn.songstats[pid]["perfect_combo"] != 0 and self.conn.songstats[pid]["perfect_combo"] % 250 == 0:
                self.conn.songstats[pid]["toasties"] += 1
            self.conn.songstats[pid]["dp"] += models.SongStat.calc_dp(stats["stepid"])
            stats["grade"] = models.SongStat.calc_grade_from_ratio( \
                self.conn.songstats[pid]["dp"] / (self.conn.songstats[pid]["taps"]*2), \
                self.conn.songstats[pid]["data"])

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


    def notesize_from_combo(self, combo, data):
        if len(data) > 0:
            if combo > 0:
                return combo - data[-1]["combo"]
            else:
                return 1
        else:
            return 1
