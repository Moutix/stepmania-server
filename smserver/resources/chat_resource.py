""" Chat resource """

from smserver import ability
from smserver import event
from smserver import exceptions
from smserver import messaging
from smserver.resources import base

class ChatResource(base.BaseResource):
    """ Chat class resource """

    def send(self, message, target=None):
        """ Send a message to the chat

            :param str message: Message send by the connection
        """

        if not self.connection.can(ability.Permissions.chat, self.connection.room_id):
            raise exceptions.Unauthorized(self.token, "Unauthorized to post message")

        command, param = self.parse_command(message)
        if command:
            return self.command(command, param)

        if not target and self.connection.room:
            target = "~{name}".format(name=self.connection.room.name)

        msg = event.Event(
            kind=event.EventKind.chat_message,
            data={
                "source": self.token,
                "message": message,
                "target": target,
                "type": "chat"
            },
            token=self.token,
        )
        if self.connection.room:
            msg.room_id = self.connection.room.id

        messaging.send(msg)

    @staticmethod
    def parse_command(message, prefix="/"):
        """ From a string get the command and value to execute

            >>> ChatResource.parse_command("/test bla")
            ('test', 'bla')

            >>> ChatResource.parse_command("/test")
            ('test', None)

            >>> ChatResource.parse_command("/test    ")
            ('test', None)

            >>> ChatResource.parse_command("/  efzef")
            (None, None)

            >>> ChatResource.parse_command("bla")
            (None, None)

            >>> ChatResource.parse_command("/test   bla   ")
            ('test', 'bla')
        """

        if not message.startswith(prefix):
            return None, None

        split = message.split(" ", 1)

        key = split[0][1:]
        if not key:
            return None, None

        if len(split) == 1:
            return key, None

        return key, split[1].strip() or None

    def command(self, command, param):
        """ Send a command """

        if command not in self.serv.chat_commands:
            raise exceptions.NotFound(self.token, "Unknown command %s" % command)

        if not self.serv.chat_commands[command].can(self.connection):
            raise exceptions.Unauthorized(self.token, "Unauthorized command %s" % command)

        return self.serv.chat_commands[command](self, param)
