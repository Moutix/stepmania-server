#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver.smutils import smpacket
from smserver.stepmania_controller import StepmaniaController
from smserver import models

class DiscoveryController(StepmaniaController):
    command = smpacket.SMClientCommand.NSCFormatted
    require_login = False

    def handle(self):
        self.send(smpacket.SMPacketServerNSCFormatted(
            server_port=self.server.config.server["port"],
            server_name=self.server.config.server["name"],
            nb_players=models.User.nb_onlines(self.session)
        ))

