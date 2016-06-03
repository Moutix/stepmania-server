#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver import pluginmanager

class ChatPlugin(pluginmanager.StepmaniaPlugin):
    COMMAND = r"/"

    def on_nsccm(self, session, serv, packet):
        pass
