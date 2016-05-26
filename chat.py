#!/usr/bin/env python3
# -*- coding: utf8 -*-

import re

from smutils import smpacket

class StepmaniaChat(object):
    def __init__(self, server):
        self.server = server

    def send(self, room, message, session):
        packet = smpacket.SMPacketServerNSCCM(message=message)
        if room:
            self.server.sendroom(room, packet)
            return

        self.server.sendall(packet)


