#!/usr/bin/env python3
# -*- coding: utf8 -*-

import re

import pluginmanager
from smutils import smpacket

class ChatPlugin(pluginmanager.StepmaniaPlugin):
    COMMAND = r"/"

    def on_nsccm(self, session, serv, packet):
        message = packet["message"]

        key, value = self.parse_message(message, self.COMMAND)

        self.on_message(session, serv, message)

    def on_message(self, session, serv, message):
        self.send_message(serv, message)

    def send_message(self, serv, message):
        packet = smpacket.SMPacketServerNSCCM(message=message)
        if serv.room:
            self.server.sendroom(serv.room, packet)
            return

        self.server.sendall(packet)

    @staticmethod
    def parse_message(message, sufix=r"/"):
        m = re.search(r'^' + sufix + r'(\S+)\s*(.*)$', message)
        if m:
            key = m.group(1).lower()
            value = m.group(2)
        else:
            key = None
            value = None

        return key, value
