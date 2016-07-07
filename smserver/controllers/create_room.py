#!/usr/bin/env python3
# -*- coding: utf8 -*-

import hashlib

from smserver.smutils import smpacket
from smserver.chathelper import with_color

from smserver.stepmania_controller import StepmaniaController
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

        self.conn.room = room.id
        for user in self.active_users:
            user.room = room
            user.set_level(room.id, 10)
            self.log.info("Player %s enter in room %s" % (user.name, room.name))

        self.send(smpacket.SMPacketServerNSSMONL(
            packet=room.to_packet()
        ))

