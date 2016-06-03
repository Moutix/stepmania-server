#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver.smutils import smpacket
from smserver import models
from smserver.chathelper import with_color

from datetime import datetime

class StepmaniaController(object):
    command = None
    require_login = False

    def __init__(self, server, conn, packet, session):
        self.server = server
        self.conn = conn
        self.packet = packet
        self.session = session
        self.log = self.server.log

        self._room = None
        self._users = None
        self._room_users = None
        self._song = None

    @property
    def room(self):
        if not self.conn.room:
            return None

        if not self._room:
            self._room = self.session.query(models.Room).get(self.conn.room)

        return self._room

    def song(self):
        if not self.conn.song:
            return None

        if not self._song:
            self._song = self.session.query(models.Song).get(self.conn.song)

        return self._song

    @property
    def users(self):
        if not self._users:
            self._users = self.server.get_users(self.conn.users, self.session)

        return self._users

    @property
    def active_users(self):
        return [user for user in self.users if user.online]

    @property
    def room_users(self):
        if not self._room_users:
            self._room_users = self.session.query(models.User).filter_by(romm_id=self.conn.room)

        return self._room_users

    @property
    def user_repr(self):
        return "<%s>" % ", ".join(user.name for user in self.users)

    def handle(self):
        pass

    def send(self, packet):
        self.conn.send(packet)

    def sendall(self, packet):
        self.server.sendall(packet)

    def sendroom(self, room, packet):
        self.server.sendroom(room, packet)

    def sendplayers(self, room, song, packet):
        self.server.sendroom(room, song, packet)

    def send_message(self, message, to=None):
        message = "[%s] %s" % (datetime.now().strftime("%X"), message)
        packet = smpacket.SMPacketServerNSCCM(message=message)

        func = {
            "me": self.send,
            "all": self.sendall,
            "room": self.sendroom
        }.get(to)

        if func == self.sendroom or (not func and self.room):
            self.sendroom(self.room.id, packet)
            return

        if func:
            func(packet)
            return

        self.server.sendall(packet)

    def send_user_message(self, message, to=None):
        self.send_message("%s: %s" % (with_color(self.user_repr), message), to)

