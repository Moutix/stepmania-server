#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smutils import smpacket

from stepmania_controller import StepmaniaController

class SMOController(StepmaniaController):
    command = smpacket.SMClientCommand.NSSMONL

    def handle(self):
        self.server.handle_packet(self.session, self.conn, self.packet["packet"])

