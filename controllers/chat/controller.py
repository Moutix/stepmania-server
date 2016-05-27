#!/usr/bin/env python3
# -*- coding: utf8 -*-

import re

from smutils import smpacket

from stepmania_controller import StepmaniaController

import models

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

    commands = {
        "help": ChatHelp(),
        "users": ChatUserListing()
    }

    def handle(self):
        message = self.packet["message"]

        key, value = self._parse_message(message)

        if key:
            self._on_command(key, value)
            return

        self.send_user_message(message)

    def _on_command(self, key, value):
        self.commands.get(key, ChatHelp)(self, value)

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


