#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver import pluginmanager, chatplugin, stepmania_controller
from smserver.smutils import smpacket

class ExampleChatPlugin(chatplugin.ChatPlugin):
    command = "coucou"

    def __call__(self, serv, message):
        print("coucou")

class ExampleGenericPlugin(pluginmanager.StepmaniaPlugin):
    def on_nsccm(self, session, serv, packet):
        print(packet)

class ExampleControllerPlugin(stepmania_controller.StepmaniaController):
    command = smpacket.SMClientCommand.NSCCM

    def handle(self):
        print(self.packet)

