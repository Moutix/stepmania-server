#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smutils import smpacket

from stepmania_controller import StepmaniaController

import models

class RoomInfoController(StepmaniaController):
    command = smpacket.SMOClientCommand.ROOMINFO

    def handle(self):
        room = self.session.query(models.Room).filter_by(name=self.packet["room"]).first()

        self.send(room.room_info)

