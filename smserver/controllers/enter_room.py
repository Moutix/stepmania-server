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

        if not self._can_enter_room(room):
            return

        self.send(smpacket.SMPacketServerNSSMONL(
            packet=room.to_packet()
        ))

        if self.conn.room == room.id:
            return

        self.server.leave_room(self.room, conn=self.conn)
        self.server.enter_room(room, conn=self.conn)

        self.send_room_resume(self.server, self.conn, room)

    def _can_enter_room(self, room):
        if not room:
            self.log.info(
                "Player %s fail to enter in room %s" % (self.conn.ip, self.packet["room"]))
            return False

        if models.Ban.is_ban(self.session, ip=self.conn.ip, room_id=room.id):
            self.log.info("Ban ip %s fail to enter in room %s" % (self.conn.ip, room.name))
            self.send_message("IP %s is ban from this room." % (with_color(self.conn.ip)), to="me")
            return False

        for user in self.active_users:
            if models.Ban.is_ban(self.session, user_id=user.id, room_id=room.id):
                self.log.info("Ban player %s fail to enter in room %s" % (user.name, room.name))
                self.send_message("Player %s is ban from this room." % (user.fullname_colored()), to="me")
                return False

        if room.nb_players >= room.max_users:
            self.log.info("Player %s can't enter in room %s, the room is full" % (user.name, room.name))
            self.send_message("Room %s is full (%s/%s) players" % (with_color(room.name), room.nb_players, room.max_users), to="me")
            return False

        return True

    @staticmethod
    def send_room_resume(server, conn, room):
        """
            Send the room welcome information.

            :param server: Main server
            :param conn: Connection target
            :param room: Room to be resume
            :type server: smserver.server.StepmaniaServer
            :type conn: smserver.smutils.smconn.StepmaniaConn
            :type room: smserver.models.room.Room
        """

        messages = []

        messages.append(
            "Room %s (%s), created at %s" % (
                with_color(room.name),
                room.mode if room.mode else "normal",
                room.created_at
            )
        )

        messages.append(
            "%s/%s players online. Moderators: %s" % (
                room.nb_players,
                room.max_users,
                ", ".join(player.fullname_colored(room.id)
                          for player in room.moderators)
            )
        )

        if room.motd:
            messages.append(room.motd)

        for message in messages:
            server.send_message(message, conn=conn)

