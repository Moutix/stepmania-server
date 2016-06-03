#!/usr/bin/env python3
# -*- coding: utf8 -*-

import hashlib

from smserver.smutils import smpacket

from smserver.stepmania_controller import StepmaniaController
from smserver import models

class CreateRoomController(StepmaniaController):
    command = smpacket.SMOClientCommand.CREATEROOM
    require_login = True

    def handle(self):
        room = models.Room(
            name=self.packet["title"],
            description=self.packet["description"],
            type=self.packet["type"],
            password=hashlib.sha256(self.packet["password"].encode('utf-8')).hexdigest() if self.packet["password"] else None,
            status=2,
        )
        self.session.add(room)
        self.session.commit()

        self.log.info("New room %s created by player %s" % (room.name, self.conn.ip))

        self.conn.room = room.id
        for user in self.active_users:
            user.room = room
            self.log.info("Player %s enter in room %s" % (user.name, room.name))

        self.send(smpacket.SMPacketServerNSSMONL(
            packet=room.to_packet()
        ))

        self.sendall(models.Room.smo_list(self.session))


