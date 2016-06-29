#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver.smutils import smpacket
from smserver.stepmania_controller import StepmaniaController
from smserver import models

class RoomInfoController(StepmaniaController):
    command = smpacket.SMOClientCommand.ROOMINFO
    require_login = True

    def handle(self):
        room = self.session.query(models.Room).filter_by(name=self.packet["room"]).first()

        self.send(room.room_info)

