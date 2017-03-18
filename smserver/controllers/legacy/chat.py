""" Chat controller main class """

from smserver import exceptions
from smserver.smutils.smpacket import smcommand
from smserver.stepmania_controller import StepmaniaController
from smserver.resources.chat_resource import ChatResource


class ChatController(StepmaniaController):
    """ Legacy chat controller """

    command = smcommand.SMClientCommand.NSCCM
    require_login = True

    def handle(self):
        """ Handle a new NSCCM command """

        chat_resource = ChatResource(
            self.server,
            self.conn.token,
            self.session
        )

        try:
            responses = chat_resource.send(message=self.packet["message"])
        except exceptions.Unauthorized:
            self.send_message("Unauthorized action.", to="me")
        except exceptions.NotFound:
            self.send_message("Unknown command. /help for available commands", to="me")

        if not responses:
            return

        for message in responses:
            self.send_message(message, to="me")
