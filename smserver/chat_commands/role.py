""" Role chat command """

from smserver import models, ability
from smserver.chathelper import with_color
from smserver.chatplugin import ChatPlugin


class ChatOP(ChatPlugin):
    """ Command to OP a user """

    command = "op"
    helper = "Change user level to operator. /op user"
    room = True
    permission = ability.Permissions.set_op

    def __call__(self, resource, message):
        user = resource.session.query(models.User).filter_by(name=message).first()
        if not user:
            return ["Unknown user %s" % with_color(message)]

        connection = resource.connection

        if user.level(connection.room_id) > connection.level(connection.room_id):
            return ["Not authorize to op %s" % user.fullname_colored(connection.room_id)]

        user.set_level(connection.room_id, 5)
        resource.send("%s give operator right to %s" % (
            models.User.colored_users_repr(connection.active_users),
            user.fullname_colored(connection.room_id)
        ))


class ChatOwner(ChatPlugin):
    """ Command to owner a user """

    command = "owner"
    helper = "Change user level to owner. /owner user"
    room = True
    permission = ability.Permissions.set_owner

    def __call__(self, resource, message):
        user = resource.session.query(models.User).filter_by(name=message).first()
        if not user:
            return ["Unknown user %s" % with_color(message)]

        connection = resource.connection

        if user.level(connection.room_id) > connection.level(connection.room_id):
            return ["Not authorize to owner %s" % user.fullname_colored(connection.room_id)]

        user.set_level(connection.room_id, 10)
        resource.send("%s give owner right to %s" % (
            models.User.colored_users_repr(connection.active_users),
            user.fullname_colored(connection.room_id)
        ))


class ChatVoice(ChatPlugin):
    """ Command to voice a user """

    command = "voice"
    helper = "Change user level to voice. /voice user"
    room = True
    permission = ability.Permissions.set_voice

    def __call__(self, resource, message):
        user = resource.session.query(models.User).filter_by(name=message).first()
        if not user:
            return ["Unknown user %s" % with_color(message)]

        connection = resource.connection

        if user.level(connection.room_id) > connection.level(connection.room_id):
            return ["Not authorize to voice %s" % user.fullname_colored(connection.room_id)]

        user.set_level(connection.room_id, 1)
        resource.send("%s give voice right to %s" % (
            models.User.colored_users_repr(connection.active_users),
            user.fullname_colored(connection.room_id)
        ))
