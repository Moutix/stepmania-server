#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver.smutils import smpacket
from smserver.stepmania_controller import StepmaniaController
from smserver import models

class LoginController(StepmaniaController):
    command = smpacket.SMOClientCommand.LOGIN
    require_login = False

    def handle(self):
        connected = self.server.auth.login(self.packet["username"], self.packet["password"])

        if not connected:
            self.log.info("Player %s failed to connect" % self.packet["username"])
            self.send(smpacket.SMPacketServerNSSMONL(
                packet=smpacket.SMOPacketServerLogin(
                    approval=1,
                    text="Connection failed for user %s" % self.packet["username"]
                )
            ))
            return

        user = models.User.connect(self.packet["username"], self.packet["player_number"], self.session)
        self.log.info("Player %s successfully connect" % self.packet["username"])

        user.last_ip = self.conn.ip
        user.stepmania_name = self.conn.stepmania_name
        user.stepmania_version = self.conn.stepmania_version

        for online_user in self.users:
            if online_user.pos == self.packet["player_number"] and online_user.name != user.name:
                online_user.pos = None
                online_user.online = False

        if user.id not in self.conn.users:
            self.conn.users.append(user.id)

        self.send(smpacket.SMPacketServerNSSMONL(
            packet=smpacket.SMOPacketServerLogin(
                approval=0,
                text="Player %s successfully login" % self.packet["username"]
            )
        ))
        self.server.send_user_list(self.session)
        self.send(models.Room.smo_list(self.session))

