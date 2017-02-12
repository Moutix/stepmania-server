""" Stepmania online controller"""

from smserver.smutils.smpacket import smcommand
from smserver.stepmania_controller import StepmaniaController

class SMOController(StepmaniaController):
    command = smcommand.SMClientCommand.NSSMONL
    require_login = False

    def handle(self):
        if not self.packet["packet"]:
            return None

        self.server.handle_packet(self.session, self.conn, self.packet["packet"])
