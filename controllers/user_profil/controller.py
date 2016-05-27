#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smutils import smpacket

from stepmania_controller import StepmaniaController

class UserProfilController(StepmaniaController):
    command = smpacket.SMClientCommand.NSCSU

    def handle(self):
        if not self.users:
            return

        for user in self.users:
            if user.pos == self.packet["player_id"]:
                user.online = True
                continue

            if self.packet["nb_players"] == 1:
                user.online = False
                self.log.info("User %s disconnected" % user.name)
                continue

            user.online = True
            self.log.info("User %s connected" % user.name)


