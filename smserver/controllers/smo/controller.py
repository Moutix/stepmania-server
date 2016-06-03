#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver.smutils import smpacket
from smserver.stepmania_controller import StepmaniaController

class SMOController(StepmaniaController):
    command = smpacket.SMClientCommand.NSSMONL
    require_login = False

    def handle(self):
        self.server.handle_packet(self.session, self.conn, self.packet["packet"])

