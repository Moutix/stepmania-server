#!/usr/bin/env python3
# -*- coding: utf8 -*-

import hashlib

from smserver.smutils import smpacket
from smserver.chathelper import with_color

from smserver.stepmania_controller import StepmaniaController
from smserver.controllers import enter_room
from smserver import models

class CreateRoomController(StepmaniaController):
    command = smpacket.SMOClientCommand.CREATEROOM
    require_login = True

    def handle(self):
        room = self.session.query(models.Room).filter_by(name=self.packet["title"]).first()
        if room:
            self.send_message("The room %s already exist! Try another name." % (with_color(self.packet["title"])))
            return

        room = models.Room(
            name=self.packet["title"],
            description=self.packet["description"],
            type=self.packet["type"],
            password=hashlib.sha256(self.packet["password"].encode('utf-8')).hexdigest() if self.packet["password"] else None,
            status=1,
        )
        self.session.add(room)
        self.session.commit()

        self.log.info("New room %s created by player %s" % (room.name, self.conn.ip))

        if self.room:
            self.server.leave_room(self.room, conn=self.conn)

        self.conn.room = room.id
        for user in self.active_users:
            user.room = room
            user.set_level(room.id, 10)
            self.log.info("Player %s enter in room %s" % (user.name, room.name))

        roomspacket = models.Room.smo_list(self.session, self.active_users)
        for conn in self.server.connections:
            if conn.room == None:
                conn.send(roomspacket)
                self.server.send_user_list_lobby(conn, self.session)
        self.send(smpacket.SMPacketServerNSSMONL(
            packet=room.to_packet()
        ))

        enter_room.EnterRoomController.send_room_resume(self.server, self.conn, room)
        self.send_message(
            "Welcome to your new room! Type /help for options", to="me"
        )


