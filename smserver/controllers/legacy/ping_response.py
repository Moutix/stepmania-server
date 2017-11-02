""" Ping response controller """

from smserver.smutils.smpacket import smcommand

from smserver.stepmania_controller import StepmaniaController

class PINGRController(StepmaniaController):
    command = smcommand.SMClientCommand.NSCPingR
    require_login = False

    def handle(self):
        """ Handle a new PINGR packet. Do nothing for the moment """
