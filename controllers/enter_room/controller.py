#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smutils import smpacket

from stepmania_controller import StepmaniaController

import models

class EnterRoomController(StepmaniaController):
    command = smpacket.SMOClientCommand.ENTERROOM

    def handle(self):
        if not self.active_users:
            self.log.info("User unknown return")
            return

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


        self.conn.room = room.id
        for user in self.active_users:
            user.room = room
            self.log.info("Player %s enter in room %s" % (user.name, room.name))

        self.send(smpacket.SMPacketServerNSSMONL(
            packet=room.to_packet()
        ))


