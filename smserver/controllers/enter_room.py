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
            self.send(models.Room.smo_list(self.session, self.active_users))
            self.conn.room = None
            for user in self.active_users:
                user.room = None

            return

        room = models.Room.login(self.packet["room"], self.packet["password"], self.session)

        if not room:
            self.log.info("Player %s fail to enter in room %s" % (self.conn.ip, self.packet["room"]))
            return

        if models.Ban.is_ban(self.session, ip=self.conn.ip, room_id=room.id):
            self.log.info("Ban ip %s fail to enter in room %s" % (self.conn.ip, room.name))
            self.send_message("IP %s is ban from this room." % (with_color(self.conn.ip)), to="me")
            return

        for user in self.active_users:
            if models.Ban.is_ban(self.session, user_id=user.id, room_id=room.id):
                self.log.info("Ban player %s fail to enter in room %s" % (user.name, room.name))
                self.send_message("Player %s is ban from this room." % (with_color(user.fullname())), to="me")
                return

        if room.nb_players >= room.max_users:
            self.log.info("Player %s can't enter in room %s, the room is full" % (user.name, room.name))
            self.send_message("Room %s is full (%s/%s) players" % (with_color(room.name), room.nb_players, room.max_users), to="me")
            return

        self.send(smpacket.SMPacketServerNSSMONL(
            packet=room.to_packet()
        ))

        if self.conn.room == room.id:
            return

        precedent_room = self.room

        self.conn.room = room.id
        self._send_room_resume(room)
        for user in self.active_users:
            if precedent_room:
                self.send_message(
                    "Player %s leave the room" % (
                        with_color(user.fullname(precedent_room.id))
                    ),
                    room_id=precedent_room.id
                )

            user.room = room
            if not user.room_privilege(room.id):
                user.set_level(room.id, 1)

            self.log.info("Player %s enter in room %s" % (user.name, room.name))
            self.send_message("%s joined the room" % (
                with_color(user.fullname(room.id))
            ))


        if precedent_room:
            self.server.send_user_list(precedent_room)

        self.server.send_user_list(room)

    def _send_room_resume(self, room):
        players = room.online_users

        self.send_message("Welcome to %s room, created at %s" % (with_color(room.name), room.created_at), to="me")
        self.send_message(
            "%s/%s players online. Moderators: %s" % (
                room.nb_players,
                room.max_users,
                ", ".join(with_color(player.fullname(room.id)) for player in players if player.level(room.id) > 2)),
            to="me")
        if room.motd:
            self.send_message(room.motd, to="me")

