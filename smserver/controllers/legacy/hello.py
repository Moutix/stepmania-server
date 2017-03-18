""" Hello controller """

from smserver.smutils.smpacket import smcommand
from smserver.smutils.smpacket import smpacket

from smserver.stepmania_controller import StepmaniaController

class HelloController(StepmaniaController):
    command = smcommand.SMClientCommand.NSCHello
    require_login = False

    def handle(self):
        """ Handle a new HELLO packet. Use to declare the version used """

        self.connection.client_version = self.packet["version"]
        self.connection.client_name = self.packet["name"]

        self.conn.send(smpacket.SMPacketServerNSCHello(
            version=128,
            name=self.server.config.server["name"]))
