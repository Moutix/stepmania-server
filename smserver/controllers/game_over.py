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
            score = self.conn.songstats[user.pos]["data"][-1]["score"]

            with self.conn.mutex:
                songstat = self.create_stats(user, self.conn.songstats[user.pos], song_duration)
                try:
                    rate = float(self.conn.songstats[user.pos]["rate"])
                except:
                    rate = 0
                if rate == 1.0:
                    rankedsong = self.session.query(models.RankedSong).filter_by(chartkey = self.conn.songstats[user.pos]["chartkey"]).first()
                    if rankedsong:
                        if float(rankedsong.taps) == songstat.taps:
                            for skillset in Skillsets:
                                ssrs = self.session.query(models.SSR).filter_by(user_id = user.id).filter_by(skillset = skillset.value).order_by(models.SSR.ssr.desc()).all()
                                rating = eval("rankedsong." + skillset.name)
                                ssr = rating * score / 9300
                                if len(ssrs) < self.server.config.server["max_ssrs"]:
                                    self.session.add(models.SSR(user_id = user.id, skillset = skillset.value, ssr = ssr, song_stat_id = songstat.id))
                                elif ssrs[0].ssr < ssr:
                                    serv.session.delete(ssrs[0])
                                    self.session.add(models.SSR(user_id = user.id, skillset = skillset.value, ssr = ssr, song_stat_id = songstat.id))
                if user.show_offset == True:
                    self.send_message(
                        "%s average offset" % self.conn.songstats[user.pos]["offsetacum"] / 
                        len(self.conn.songstats[user.pos]["data"]),
                        to="me")
            xp = songstat.calc_xp(self.server.config.score.get("xpWeight"))
            user.xp += xp

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
        self.session.commit()

        return songstat

