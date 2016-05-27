#!/usr/bin/env python3
# -*- coding: utf8 -*-

import re

import pluginmanager
from smutils import smpacket

class ChatPlugin(pluginmanager.StepmaniaPlugin):
    COMMAND = r"/"

    def on_nsccm(self, session, serv, packet):
        pass
