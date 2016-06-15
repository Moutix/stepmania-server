#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from smserver.smutils import smpacket
from smserver.stepmania_controller import StepmaniaController
from smserver import models

class StartGameRequestController(StepmaniaController):
    command = smpacket.SMClientCommand.NSCGSR
    require_login = True

    def handle(self):
        if not self.room:
            return

        if self.room.status != 2:
            return

        song = models.Song.find_or_create(
            self.packet["song_title"],
            self.packet["song_subtitle"],
            self.packet["song_artist"],
            self.session)

        with self.conn.mutex:
            self.conn.song_id = song.id
            self.conn.songs[song.id] = True

            self.conn.songstats = {
                0: {"data": [],
                    "feet": self.packet["first_player_feet"],
                    "difficulty": self.packet["first_player_difficulty"],
                    "options": self.packet["first_player_options"],
                    "best_score": song.best_score_value(self.packet["first_player_feet"])
                   },
                1: {"data": [],
                    "feet": self.packet["second_player_feet"],
                    "difficulty": self.packet["second_player_difficulty"],
                    "options": self.packet["second_player_options"],
                    "best_score": song.best_score_value(self.packet["second_player_feet"])
                   },
                "start_at": datetime.datetime.now(),
                "options": self.packet["song_options"],
                "course_title": self.packet["course_title"]
                }


            self.conn.wait_start = True

        for player in self.server.room_connections(self.room.id):
            if player.wait_start is False:
                return

        self.launch_song(self.room, song, self.server)

    @staticmethod
    def launch_song(room, song, server):
        room.active_song = song
        room.ingame = True
        server.log.info("Room %s start a new song %s" % (room.name, song.fullname))

        for player in server.ingame_connections(room.id):
            with player.mutex:
                player.songstats["start_at"] = datetime.datetime.now()
                player.wait_start = False
                player.ingame = True

            player.send(smpacket.SMPacketServerNSCGSR())

