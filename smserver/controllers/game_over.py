#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from smserver.smutils import smpacket
from smserver.stepmania_controller import StepmaniaController
from smserver import models
from smserver.models import ranked_song
from smserver.models.ranked_song import Skillsets

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
            taps = self.conn.songstats[user.pos]["taps"]
            migs = 0
            for update in self.conn.songstats[user.pos]["data"]:
                migs += self.migs(update["stepid"])
            if taps > 0:
                dppercent = (self.conn.songstats[user.pos]["dpacum"] * 100 
                    / (self.conn.songstats[user.pos]["taps"] * 2
                     + self.conn.songstats[user.pos]["holds"] * 6))
                migspercent = (migs * 100 
                    / (self.conn.songstats[user.pos]["taps"] * 4
                     + self.conn.songstats[user.pos]["holds"] * 6))
            else:
                dppercent = 0
                migspercent = 0
            with self.conn.mutex:
                songstat = self.create_stats(user, self.conn.songstats[user.pos], song_duration)
                rate = self.conn.songstats[user.pos]["rate"]
                if rate == 100:
                    chartkey = self.conn.songstats[user.pos]["chartkey"]
                    if chartkey != None:
                        rankedsong = (self.session.query(models.RankedSong)
                            .filter_by(chartkey = chartkey).first())
                        if rankedsong:
                            if rankedsong.taps == taps:
                                for skillset in Skillsets:
                                    rating = eval("rankedsong." + skillset.name)
                                    ssr = rating * dppercent / 100
                                    repeated = (self.session.query(models.SSR)
                                        .filter_by(user_id = user.id)
                                        .filter_by(skillset = skillset.value)
                                        .filter_by(chartkey = chartkey).first())
                                    if not repeated:
                                        ssrs = (self.session.query(models.SSR)
                                            .filter_by(user_id = user.id)
                                            .filter_by(skillset = skillset.value)
                                            .order_by(models.SSR.ssr.desc()).all())
                                        if len(ssrs) >= self.server.config.server["max_ssrs"]:
                                            if ssrs[0].ssr < ssr:
                                                self.session.delete(ssrs[0])
                                            else:
                                                continue
                                    else:
                                        if repeated.ssr < ssr:
                                            self.session.delete(repeated)
                                        else:
                                            continue
                                    self.session.add(models.SSR(
                                        user_id = user.id, skillset = skillset.value,
                                        ssr = ssr, song_stat_id = songstat.id,
                                        song_id = self.room.active_song.id,
                                        chartkey = chartkey))
                                    user.updaterating(self.session, skillset)


                if user.show_offset == True:
                    if taps > 0:
                        self.send_message(
                            "%s average offset" % 
                            str(self.conn.songstats[user.pos]["offsetacum"] / taps)[:5],
                            to="me")
            xp = songstat.calc_xp(self.server.config.score.get("xpWeight"))
            user.xp += xp

            if self.conn.songstats[user.pos]["toasties"] > 0:
                toasty = True
            else:
                toasty = False
            self.session.commit()
            self.send_message("New result: %s" % 
                songstat.pretty_result(room_id=self.room.id,
                color=True, date=False, toasty=toasty) + 
                songstat.showbests(user.id, self.room.active_song.id))

            self.send_message(
                "%s gained %s XP!" % (
                    user.fullname_colored(user.room_id),
                    with_color(xp, "aaaa00")
                    ),
                to="me")


        with self.conn.mutex:
            self.conn.ingame = False
            self.conn.songstats = {0: {"data": []}, 1: {"data": []}}
            self.conn.song = None

    def create_stats(self, user, raw_stats, duration):
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
            dp =raw_stats["dpacum"]
        )
        songstat.migsp = 0
        for stepid in models.SongStat.stepid.values():
            setattr(songstat, stepid, 0)
        for value in raw_stats["data"]:
            songstat.migsp += self.migs(value["stepid"])
            if value["combo"] > songstat.max_combo:
                songstat.max_combo = value["combo"]

            if value["stepid"] not in models.SongStat.stepid:
                continue

            setattr(songstat,
                    models.SongStat.stepid[value["stepid"]],
                    getattr(songstat, models.SongStat.stepid[value["stepid"]]) + 1
                   )

        if raw_stats["taps"] > 0:
            songstat.percentage = songstat.dp * 100 / (raw_stats["taps"] * 2 + raw_stats["holds"] * 6)
        else:
            songstat.percentage  = 0

        if raw_stats["taps"] > 0:
            songstat.migs = songstat.migsp * 100 / (raw_stats["taps"] * 4 + raw_stats["holds"] * 6)
        else:
            songstat.migs  = 0

        if raw_stats["data"]:
            songstat.grade = self.grade(songstat.percentage, raw_stats["data"])
            songstat.score = raw_stats["data"][-1]["score"]

        songstat.raw_stats = models.SongStat.encode_stats(raw_stats["data"])

        self.session.add(songstat)

        return songstat

    def grade(self, score, data):
        if score >= 100.00:
            for note in data:
                if note["stepid"] > 2 and note["stepid"] < 9:
                    if note != 9:
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

    def showbests(self, user, songstat):
        tbs = (self.session.query(models.SongStat)
            .filter_by(song_id = self.room.active_song.id)
            .filter_by(difficulty = songstat.difficulty)
            .order_by(models.SongStat.dp.asc()).all())
        pbs = (self.session.query(models.SongStat)
            .filter_by(user_id = user.id)
            .filter_by(song_id = self.room.active_song.id)
            .filter_by(difficulty = songstat.difficulty)
            .order_by(models.SongStat.dp.asc()).all())

        for count, tb in enumerate(tbs, 1):
            if tb == songstat:
                tbcount = count
                break
        for count, pb in enumerate(pbs, 1):
            if pb == songstat:
                pbcount = count
                break

        return (" PB: " + str(tbcount) + "/" + str(len(tbs)) + " TB: " + str(pbcount) + "/" + str(len(pbs)))


    def migs(self, stepsid):
        if stepsid == 8:
            return 4
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