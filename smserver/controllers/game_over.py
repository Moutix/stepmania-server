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
            taps = self.conn.songstats[user.pos]["taps"]
            if taps > 0:
                score = self.conn.songstats[user.pos]["dpacum"] * 100 / (self.conn.songstats[user.pos]["taps"] * 2 + self.conn.songstats[user.pos]["holds"] * 6)
            else:
                score = 0
            with self.conn.mutex:
                if self.conn.songstats[user.pos]["data"]:
                    if score > 0:
                        self.conn.songstats[user.pos]["data"][-1]["score"] = int(score*100)
                    else:
                        self.conn.songstats[user.pos]["data"][-1]["score"] = 0
                    self.conn.songstats[user.pos]["data"][-1]["grade"] = self.grade(score, self.conn.songstats[user.pos]["data"])
                songstat = self.create_stats(user, self.conn.songstats[user.pos], song_duration)
                rate = self.conn.songstats[user.pos]["rate"]
                if rate == 100:
                    rankedsong = self.session.query(models.RankedSong).filter_by(chartkey = self.conn.songstats[user.pos]["chartkey"]).first()
                    if rankedsong:
                        if rankedsong.taps == taps:
                            for skillset in Skillsets:
                                rating = eval("rankedsong." + skillset.name)
                                ssr = rating * score / 100
                                repeated = self.session.query(models.SSR).filter_by(user_id = user.id).filter_by(skillset = skillset.value).filter_by(song_id = self.room.active_song.id).first()
                                if not repeated:
                                    ssrs = self.session.query(models.SSR).filter_by(user_id = user.id).filter_by(skillset = skillset.value).order_by(models.SSR.ssr.desc()).all()
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
                                self.session.add(models.SSR(user_id = user.id, skillset = skillset.value, ssr = ssr, song_stat_id = songstat.id, song_id = self.room.active_song.id))
                                if skillset.value == 0:
                                    user.updaterating(self.session)


                if user.show_offset == True:
                    self.send_message(
                        "%s average offset" % str(self.conn.songstats[user.pos]["offsetacum"] / taps)[:5], to="me")
            xp = songstat.calc_xp(self.server.config.score.get("xpWeight"))
            user.xp += xp


            self.session.commit()
            self.send_message("New result: %s" % songstat.pretty_result(room_id=self.room.id, color=True))

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
        )

        if raw_stats["data"]:
            songstat.grade = raw_stats["data"][-1]["grade"]
            songstat.score = raw_stats["data"][-1]["score"]

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

        songstat.percentage = songstat.calc_percentage(self.server.config.score.get("percentWeight"))
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
        elif score >= 0.0:
            return 6
        return 7

