#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime

from smutils import smpacket

from stepmania_controller import StepmaniaController
import models

class StartGameRequestController(StepmaniaController):
    command = smpacket.SMClientCommand.NSCGSR

    def handle(self):
        if not self.room:
            return

        song = models.Song.find_or_create(
            self.packet["song_title"],
            self.packet["song_subtitle"],
            self.packet["song_artist"],
            self.session)

        with self.conn.mutex:
            self.conn.song_id = song.id

        with self.conn.mutex:
            self.conn.songs = {
                0: {"data": [],
                    "feet": self.packet["first_player_feet"],
                    "difficulty": self.packet["first_player_difficulty"],
                    "options": self.packet["first_player_options"],
                    },
                1: {"data": [],
                    "feet": self.packet["second_player_feet"],
                    "difficulty": self.packet["second_player_difficulty"],
                    "options": self.packet["second_player_options"],
                    },
                "start_at": datetime.datetime.now(),
                "options": self.packet["song_options"],
                "course_title": self.packet["course_title"]
                }

        self.send(smpacket.SMPacketServerNSCGSR())

