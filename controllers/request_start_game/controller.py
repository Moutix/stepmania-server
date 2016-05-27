#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smutils import smpacket

from stepmania_controller import StepmaniaController

import models

class RequestStartGameController(StepmaniaController):
    command = smpacket.SMClientCommand.NSCRSG

    def handle(self):
        if not self.room:
            return

        song = models.Song.find_or_create(
            self.packet["song_title"],
            self.packet["song_subtitle"],
            self.packet["song_artist"],
            self.session)

        if self.packet["usage"] == 2:
            #TODO: Handle permission, for now just ask to start the song
            self.sendroom(self.room.id, smpacket.SMPacketServerNSCRSG(
                usage=3,
                song_title=song.title,
                song_subtitle=song.subtitle,
                song_artist=song.artist
                ))


