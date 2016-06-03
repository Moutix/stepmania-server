#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver.smutils import smpacket
from smserver.stepmania_controller import StepmaniaController
from smserver.chathelper import with_color
from smserver import models

class RequestStartGameController(StepmaniaController):
    command = smpacket.SMClientCommand.NSCRSG
    require_login = True

    def handle(self):
        if not self.room:
            return

        song = models.Song.find_or_create(
            self.packet["song_title"],
            self.packet["song_subtitle"],
            self.packet["song_artist"],
            self.session)

        if self.packet["usage"] == 2:
            self.start_game_request(song)
            return

        self.check_song_presence(song)

    def start_game_request(self, song):
        with self.conn.mutex:
            self.conn.songs[song.id] = True

        if self.conn.song == song.id:
            self.launch_song(song)
            return

        self.send_message("%s select %s" % (with_color(self.user_repr), with_color(song.title)))

        with self.conn.mutex:
            self.conn.song = song.id
            self.conn.songs[song.id] = True

        self.sendroom(self.room.id, smpacket.SMPacketServerNSCRSG(
            usage=1,
            song_title=song.title,
            song_subtitle=song.subtitle,
            song_artist=song.artist
            ))

    def check_song_presence(self, song):
        with self.conn.mutex:
            self.conn.songs[song.id] = {0: True, 1: False}[self.packet["usage"]]

    def launch_song(self, song):
        self.room.active_song = song
        self.sendroom(self.room.id, smpacket.SMPacketServerNSCRSG(
            usage=2,
            song_title=song.title,
            song_subtitle=song.subtitle,
            song_artist=song.artist
            ))

