#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver.smutils import smpacket
from smserver import models, ability
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

    def user_repr(self, room_id=None):
        return "%s" % " & ".join(user.fullname(room_id) for user in self.active_users)

    def colored_user_repr(self, room_id=None):
        return "%s" % " & ".join(with_color(user.fullname(room_id)) for user in self.active_users)

    def level(self, room_id):
        return max(user.level(room_id) for user in self.active_users)

    def can(self, action, room_id=None):
        return ability.Ability.can(action, self.level(room_id))

    def cannot(self, action, room_id=None):
        return ability.Ability.cannot(action, self.level(room_id))

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

    def send_message(self, message, to=None, room_id=None):

        func = {
            "me": self.send,
            "all": self.sendall,
            "room": self.sendroom
        }.get(to)

        if func == self.sendroom or (not func and self.room) or room_id:
            room = self.session.query(models.Room).get(room_id) if room_id else self.room
            message = "[%s] #%s %s" % (datetime.now().strftime("%X"), with_color(room.name), message)
            packet = smpacket.SMPacketServerNSCCM(message=message)
            self.sendroom(room.id, packet)
            return

        message = "[%s] %s" % (datetime.now().strftime("%X"), message)
        packet = smpacket.SMPacketServerNSCCM(message=message)

        if func:
            func(packet)
            return

        self.server.sendall(packet)

    def send_user_message(self, message, to=None):
        self.send_message(
            "%s %s" % (
                self.colored_user_repr(self.conn.room),
                message),
            to)

