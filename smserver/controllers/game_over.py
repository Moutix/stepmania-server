#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from smserver.smutils import smpacket
from smserver.stepmania_controller import StepmaniaController
from smserver import models
from smserver.models import ranked_chart
from smserver.models import song_stat

from smserver.chathelper import with_color


class GameOverController(StepmaniaController):
    command = smpacket.SMClientCommand.NSCGON
    require_login = True

    def handle(self):
        if not self.room:
            return

        if "start_at" not in self.conn.songstats:
            return

        song_duration = datetime.datetime.now() - self.conn.songstats["start_at"]

        for user in self.active_users:
            user.status = 2
            ssr = 0
            with self.conn.mutex:
                print(self.conn.songstats[user.pos]["chartkey"])
                if self.conn.songstats[user.pos]["taps"] > 0:
                    self.conn.songstats[user.pos]["dppercent"] = (self.conn.songstats[user.pos]["dp"] * 100 
                        / (self.conn.songstats[user.pos]["taps"] * 2))
                else:
                    self.conn.songstats[user.pos]["dppercent"] = 0
                rate = self.conn.songstats[user.pos]["rate"]
                if rate == 100:
                    if self.conn.songstats[user.pos]["dppercent"] >= 93:
                        chartkey = self.conn.songstats[user.pos]["chartkey"]
                        if chartkey != None:
                            rankedchart = (self.session.query(models.RankedChart)
                                .filter_by(chartkey = chartkey).first())
                            if rankedchart:
                                if (rankedchart.taps == self.conn.songstats[user.pos]["taps"] and 
                                rankedchart.jumps == self.conn.songstats[user.pos]["jumps"] and 
                                rankedchart.hands == self.conn.songstats[user.pos]["hands"]):
                                    ssr = rankedchart.rating * self.conn.songstats[user.pos]["dppercent"] / 95
                songstat = self.create_stats(user, self.conn.songstats[user.pos], song_duration, self.conn.songstats["filehash"], ssr)
                
                if user.show_offset == True:
                    if self.conn.songstats[user.pos]["taps"] > 0:
                        self.send_message(
                            "%s average offset" % 
                            str(self.conn.songstats[user.pos]["offsetacum"] / 
                            self.conn.songstats[user.pos]["taps"])[:5],
                            to="me")
                if ssr > 0:
                    query = self.session.query(models.SongStat).filter_by(user_id = user.id).order_by(models.SongStat.ssr.desc()).limit(25)
                    if query.first() and ssr > query[-1].ssr:
                        user.rating = user.updaterating(self.session)
                            
            xp = songstat.calc_xp(self.server.config.score.get("xpWeight"))
            user.xp += xp

            self.session.commit()
            self.send_message( 
                (songstat.pretty_result(room_id=self.room.id,
                color=True, date=False, toasty=True, points=self.room.show_points, userfirst=True) + 
                songstat.get_rank(user.id, self.room.active_song.id) ) + 
                " " + with_color(xp, "aaaa00") +" XP gained" + (" Score Rating : %12.2f" % ssr if ssr > 0 else ""))
            user.toastycount =+ self.conn.songstats[user.pos]["toasties"]



        with self.conn.mutex:
            self.conn.ingame = False
            self.conn.songstats = {0: {"data": []}, 1: {"data": []}}
            self.conn.song = None

    def create_stats(self, user, raw_stats, duration, filehash, ssr):
        songstat = models.SongStat(
            song_id=self.room.active_song.id,
            user_id=user.id,
            game_id=self.room.last_game.id,
            duration=duration.seconds,
            max_combo=0,
            feet=raw_stats["feet"],
            difficulty=raw_stats["difficulty"],
            options=raw_stats["options"],
            toasty=raw_stats["toasties"],
            filehash=filehash,
            chartkey=raw_stats["chartkey"],
            migsp=raw_stats["migsp"],
            rate=raw_stats["rate"],
            ssr=ssr
        )
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

        if raw_stats["taps"] > 0:
            songstat.migs = songstat.migsp * 100 / (raw_stats["taps"] * 3 + raw_stats["holds"] * 6)
        else:
            songstat.migs  = 0

        if raw_stats["data"]:
            songstat.grade = self.grade(self.conn.songstats[user.pos]["dppercent"], raw_stats["data"])
            songstat.score = raw_stats["data"][-1]["score"]

        songstat.raw_stats = models.SongStat.encode_stats(raw_stats["data"])

        self.session.add(songstat)

        return songstat

    def grade(self, score, data):
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
