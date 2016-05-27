#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smutils import smpacket

from stepmania_controller import StepmaniaController

class HelloController(StepmaniaController):
    command = smpacket.SMClientCommand.NSCHello

    def handle(self):
        self.conn.stepmania_version = self.packet["version"]
        self.conn.stepmania_name = self.packet["name"]

        self.conn.send(smpacket.SMPacketServerNSCHello(
            version=128,
            name=self.server.config.server["name"]))

