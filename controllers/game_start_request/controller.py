#!/usr/bin/env python3
# -*- coding: utf8 -*-

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

        self.send(smpacket.SMPacketServerNSCGSR())

