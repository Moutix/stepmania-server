#!/usr/bin/env python3
# -*- coding: utf8 -*-

import pluginmanager
from smutils import smpacket

class ChatPlugin(pluginmanager.StepmaniaPlugin):
    def on_nsccm(self, session, serv, packet):
        self.server.sendall(smpacket.SMPacketServerNSCCM(message=packet["message"]))
