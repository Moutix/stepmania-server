#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver.smutils import smpacket

from smserver.stepmania_controller import StepmaniaController

from smserver import models
from smserver.chathelper import with_color

class EnterRoomController(StepmaniaController):
    command = smpacket.SMOClientCommand.ENTERROOM
    require_login = True

    def handle(self):
        if self.packet["enter"] == 0:
            self.send(models.Room.smo_list(self.session))
            self.conn.room = None
            for user in self.active_users:
                user.room = None

            return

        room = models.Room.login(self.packet["room"], self.packet["password"], self.session)

        if not room:
            self.log.info("Player %s fail to enter in room %s" % (self.conn.ip, self.packet["room"]))
            return

        self.send(smpacket.SMPacketServerNSSMONL(
            packet=room.to_packet()
        ))


        if self.conn.room == room.id:
            return

        precedent_room = self.conn.room

        self.conn.room = room.id
        self._send_room_resume(room)
        for user in self.active_users:
            if precedent_room:
                self.send_message(
                    "Player %s leave the room" % (
                        with_color(user.fullname(precedent_room))
                    ),
                    room_id=precedent_room
                )

            user.room = room
            if not user.room_privilege(room.id):
                user.set_level(room.id, 1)

            self.log.info("Player %s enter in room %s" % (user.name, room.name))
            self.send_message("%s joined the room" % (
                with_color(user.fullname(self.conn.room))
            ))

    def _send_room_resume(self, room):
        players = [user for user in self.users if user.online]

        self.send_message("Welcome to %s room, created at %s" % (with_color(room.name), room.created_at), to="me")
        self.send_message(
            "%s players online. Moderators: %s" % (
                len(players),
                ", ".join(with_color(player.fullname(room.id)) for player in players if player.level(room.id) > 2)),
            to="me")
        if room.motd:
            self.send_message(room.motd, to="me")

