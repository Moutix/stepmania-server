#!/usr/bin/env python3
# -*- coding: utf8 -*-

import re

from smserver.smutils import smpacket
from smserver.stepmania_controller import StepmaniaController
from smserver import models

class ChatHelp(object):
    helper = "Show help"

    def __call__(self, serv, message):
        for command, action in serv.commands.items():
            serv.send_message("/%s: %s" % (command, action.helper), to="me")

class ChatUserListing(object):
    helper = "Show users"

    def __call__(self, serv, message):
        users = serv.session.query(models.User).filter_by(online=True)
        if serv.room:
            users = users.filter_by(room_id=serv.room.id)

        users = users.all()

        for user in users:
            serv.send_message("%s" % user.name, to="me")


class ChatController(StepmaniaController):
    command = smpacket.SMClientCommand.NSCCM
    require_login = True

    commands = {
        "help": ChatHelp(),
        "users": ChatUserListing()
    }

    def handle(self):
        message = self.packet["message"]

        key, value = self._parse_message(message)

        if not key:
            self.send_user_message(message)
            return

        if key not in self.commands:
            self.send_message("%s: Unknown command. /help for available commands" % key)
            return

        self.commands[key](self, value)

    @staticmethod
    def _parse_message(message, sufix=r"/"):
        m = re.search(r'^' + sufix + r'(\S+)\s*(.*)$', message)
        if m:
            key = m.group(1).lower()
            value = m.group(2)
        else:
            key = None
            value = None

        return key, value

