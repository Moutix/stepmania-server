#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver.smutils import smpacket
from smserver.stepmania_controller import StepmaniaController

class UserProfilController(StepmaniaController):
    command = smpacket.SMClientCommand.NSCSU
    require_login = False

    def handle(self):
        if not self.users:
            return

        for user in self.users:
            if self.packet["nb_players"] == 1 and self.packet["player_id"] != user.pos:
                self.disconnect_user(user)
                continue

            self.reconnect_user(user)

        self.server.send_sd_running_status()

        if self.conn.room:
            self.server.send_user_list(self.room)

    def reconnect_user(self, user):
        if user.online:
            return

        user.online = True
        self.session.commit()
        self.server.enter_room(self.room, conn=self.conn)
        self.log.info("User %s connected" % user.name)

    def disconnect_user(self, user):
        if not user.online:
            return

        user.online = False
        self.log.info("User %s disconnected" % user.name)
        user.room = None
        if self.room:
            self.send_message("%s leave the room" % user.fullname_colored(self.room.id))

