#!/usr/bin/env python3
# -*- coding: utf8 -*-

import pluginmanager
from smutils import smpacket

class ChatPlugin(pluginmanager.StepmaniaPlugin):
    def _on_nsccms(self, session, serv, packet):
        self.server.sendall(smpacket.SMPacketServerNSCCM(message="|c0%s" % packet["message"]))
