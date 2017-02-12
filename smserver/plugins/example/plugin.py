""" Plugin example """

from smserver import pluginmanager, chatplugin, stepmania_controller
from smserver.smutils.smpacket import smcommand

class ExampleChatPlugin(chatplugin.ChatPlugin):
    command = "coucou"

    def __call__(self, serv, message):
        print("coucou")

class ExampleGenericPlugin(pluginmanager.StepmaniaPlugin):
    def on_nsccm(self, session, serv, packet):
        print(packet)

class ExampleControllerPlugin(stepmania_controller.StepmaniaController):
    command = smcommand.SMClientCommand.NSCCM

    def handle(self):
        print(self.packet)
