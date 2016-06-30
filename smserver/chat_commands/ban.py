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
            serv.send_message("Not authorize to ban %s" % with_color(user.fullname(serv.conn.room)), to="me")
            return

        models.Ban.ban(serv.session, user_id=user.id, room_id=serv.conn.room)
        for conn in serv.server.connections:
            if user.id in conn.users:
                conn.room = None

        serv.send_message("User %s has been ban from this room" % with_color(user.fullname(serv.conn.room)))
        user.room = None
        serv.server.send_user_list(serv.room)


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
        serv.send_message("User %s has been unban from this room" % with_color(user.fullname(serv.conn.room)))

