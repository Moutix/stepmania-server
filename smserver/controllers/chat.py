""" Chat controller main class """

import re

from smserver.smutils.smpacket import smcommand
from smserver.stepmania_controller import StepmaniaController


class ChatController(StepmaniaController):
    command = smcommand.SMClientCommand.NSCCM
    require_login = True

    def handle(self):
        message = self.packet["message"]

        key, value = self._parse_message(message)

        if not key:
            self.send_user_message(message)
            return

        if key not in self.server.chat_commands:
            self.send_message("%s: Unknown command. /help for available commands" % key, to="me")
            return

        if not self.server.chat_commands[key].can(self):
            self.send_message("%s: Unauthorized action." % key, to="me")
            return

        self.server.chat_commands[key](self, value)

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
