""" Chat ban module """

from smserver import ability
from smserver import models
from smserver.resources import room_resource
from smserver.chathelper import with_color
from smserver.chatplugin import ChatPlugin


class ChatBan(ChatPlugin):
    """ Command to ban a user """

    command = "ban"
    helper = "Ban a user. /ban user"
    permission = ability.Permissions.ban_user

    def __call__(self, resource, message):
        user = resource.session.query(models.User).filter_by(name=message).first()
        connection = resource.connection

        if not user:
            return ["Unknown user %s" % with_color(message)]

        if user.level(connection.room_id) >= connection.level(connection.room_id):
            return ["Not authorize to ban %s" % user.fullname_colored(connection.room_id)]

        models.Ban.ban(resource.session, user_id=user.id, room_id=connection.room_id)
        ChatKick.kick_user(self.server, user, connection.room)

        resource.send(
            "%s ban user %s" % (
                models.User.colored_users_repr(connection.active_users),
                connection.room_id
            )
        )


class ChatKick(ChatPlugin):
    """ Command to kick a user """

    command = "kick"
    helper = "kick a user. /kick user"
    permission = ability.Permissions.kick_user

    def __call__(self, resource, message):
        user = resource.session.query(models.User).filter_by(name=message).first()
        connection = resource.connection

        if not user:
            return ["Unknown user %s" % with_color(message)]

        if user.level(connection.room_id) >= connection.level(connection.room_id):
            return ["Not authorize to kick %s" % user.fullname_colored(connection.room_id)]

        ChatKick.kick_user(self.server, user, connection.room)

        resource.send(
            "%s kick user %s" % (
                models.User.colored_users_repr(connection.active_users),
                connection.room_id
            )
        )

    @staticmethod
    def kick_user(server, user, room=None):
        """
            Kick a user from a room or server if no room provided

            :param user: User to kick
            :param room: Room where the user have to be kick
            :type user: smserver.models.user.User
            :type room: smserver.models.room.Room
        """

        if not room:
            return server.disconnect_user(user.id)

        if user.room != room:
            return

        room_resource.RoomResource(server, connection=user.connection).leave()

class ChatUnBan(ChatPlugin):
    """ Chat command to unban a user """

    command = "unban"
    helper = "UnBan a user. /unban user"
    permission = ability.Permissions.unban_user

    def __call__(self, resource, message):
        user = resource.session.query(models.User).filter_by(name=message).first()
        if not user:
            return ["Unknown user %s" % with_color(message)]

        connection = resource.connection

        models.Ban.unban(resource.session, user_id=user.id, room_id=connection.room_id)
        resource.send(
            "User {user} has been unban from this room".format(
                user=user.fullname_colored(resource.connection.room_id)
            )
        )
