""" General Chat command to handle """

from smserver import models
from smserver.chatplugin import ChatPlugin


class ChatHelp(ChatPlugin):
    """ Display the list of all the commands """

    command = "help"
    helper = "Show help"

    def __call__(self, resource, message):
        response = []

        commands = self.server.chat_commands

        if message:
            if message not in commands or not commands[message].can(resource.connection):
                return ["Unknown command %s" % message]

            return ["/%s: %s" % (message, commands[message].helper)]

        for command, action in sorted(commands.items()):
            if not action.can(resource.connection):
                continue

            response.append("/%s: %s" % (command, action.helper))

        return response

class ChatUserListing(ChatPlugin):
    """ List the users connected """

    command = "users"
    helper = "List users"

    def __call__(self, resource, message, *, limit=20):
        response = []

        connection = resource.connection

        users = resource.session.query(models.User).filter_by(online=True)
        max_users = self.server.config.server.get("max_users")
        if connection.room:
            users = users.filter_by(room_id=connection.room_id)
            max_users = connection.room.max_users

        response.append("%s/%s players online" % (users.count(), max_users))

        for user in users.order_by("name").limit(limit):
            response.append(
                "%s (in %s)" % (
                    user.fullname_colored(connection.room_id),
                    user.enum_status.name
                )
            )
        return response

class ChatTimestamp(ChatPlugin):
    """ Add the timestamp in the chat messages """

    command = "timestamp"
    helper = "Show timestamp"

    def __call__(self, serv, message):
        #FIXME need to be store elsewhere (don't work for the moment)

        if serv.conn.chat_timestamp:
            serv.conn.chat_timestamp = False
            serv.send_message("Chat timestamp disabled", to="me")
        else:
            serv.send_message("Chat timestamp enabled", to="me")
            serv.conn.chat_timestamp = True

        for user in serv.active_users:
            user.chat_timestamp = serv.conn.chat_timestamp
