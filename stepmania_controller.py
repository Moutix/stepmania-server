#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smutils import smpacket

class StepmaniaController(object):
    command = None

    def __init__(self, server, conn, packet, session):
        self.server = server
        self.conn = conn
        self.packet = packet
        self.session = session
        self.log = self.server.log

        self.room = self.server.get_room(conn.room, session)
        self.users = self.server.get_users(conn.users, session)
        self.active_users = [user for user in self.users if user.online]

    @property
    def user_repr(self):
        return ", ".join(user.name for user in self.users)

    def handle(self):
        pass

    def send(self, packet):
        self.conn.send(packet)

    def sendall(self, packet):
        self.server.sendall(packet)

    def sendroom(self, room, packet):
        self.server.sendroom(room, packet)

    def send_message(self, message, to=None):
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
        self.send_message("<%s> %s" % (self.user_repr, to))

