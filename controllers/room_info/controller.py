#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smutils import smpacket

from stepmania_controller import StepmaniaController

class RoomInfoController(StepmaniaController):
    command = smpacket.SMOClientCommand.ROOMINFO

    def handle(self):
        pass

