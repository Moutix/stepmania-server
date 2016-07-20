#!/usr/bin/env python3
# -*- coding: utf8 -*-


from smserver import models, ability
from smserver.chathelper import with_color
from smserver.chatplugin import ChatPlugin


class ChatBan(ChatPlugin):
    command = "ban"
    helper = "Ban a user. /ban user"
    permission = ability.Permissions.ban_user

    def __call__(self, serv, message):
        user = serv.session.query(models.User).filter_by(name=message).first()
        if not user:
            serv.send_message("Unknown user %s" % with_color(message), to="me")
            return

        if user.level(serv.conn.room) > serv.level(serv.conn.room):
            serv.send_message("Not authorize to ban %s" % user.fullname_colored(serv.conn.room), to="me")
            return

        models.Ban.ban(serv.session, user_id=user.id, room_id=serv.conn.room)
        ChatKick.kick_user(serv.server, user, serv.room)

        serv.server.send_message(
            "%s ban user %s" % (
                serv.colored_user_repr(serv.room),
                user.fullname_colored(serv.room)
            ),
            room=serv.room
        )


class ChatKick(ChatPlugin):
    command = "kick"
    helper = "kick a user. /kick user"
    permission = ability.Permissions.kick_user

    def __call__(self, serv, message):
        user = serv.session.query(models.User).filter_by(name=message).first()
        if not user:
            serv.send_message("Unknown user %s" % with_color(message), to="me")
            return

        if user.level(serv.conn.room) > serv.level(serv.conn.room):
            serv.send_message("Not authorize to kick %s" % user.fullname_colored(serv.conn.room), to="me")
            return

        ret = self.kick_user(serv.server, user, serv.room)
        if not ret:
            serv.send_message("Cannot kick user %s" % user.fullname_colored(serv.conn.room))
            return

        serv.server.send_message(
            "%s kick user %s" % (
                serv.colored_user_repr(serv.room),
                user.fullname_colored(serv.room)
            ),
            room=serv.room
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

        return server.leave_room(room, user.id)


class ChatUnBan(ChatPlugin):
    command = "unban"
    helper = "UnBan a user. /unban user"
    permission = ability.Permissions.unban_user

    def __call__(self, serv, message):
        user = serv.session.query(models.User).filter_by(name=message).first()
        if not user:
            serv.send_message("Unknown user %s" % with_color(message), to="me")
            return

        models.Ban.unban(serv.session, user_id=user.id, room_id=serv.conn.room)
        serv.send_message("User %s has been unban from this room" % user.fullname_colored(serv.conn.room))

