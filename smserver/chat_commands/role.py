#!/usr/bin/env python3
# -*- coding: utf8 -*-


from smserver import models, ability
from smserver.chathelper import with_color
from smserver.chatplugin import ChatPlugin


class ChatOP(ChatPlugin):
    command = "op"
    helper = "Change user level to operator. /op user"
    room = True
    permission = ability.Permissions.set_op

    def __call__(self, serv, message):
        user = serv.session.query(models.User).filter_by(name=message).first()
        if not user:
            serv.send_message("Unknown user %s" % with_color(message), to="me")
            return

        if user.level(serv.conn.room) > serv.level(serv.conn.room):
            serv.send_message("Not authorize to op %s" % with_color(user.fullname(serv.conn.room)), to="me")
            return

        user.set_level(serv.room.id, 5)
        serv.send_message("%s give operator right to %s" % (
            serv.colored_user_repr(serv.room.id),
            with_color(user.fullname(serv.room.id))
        ))


class ChatOwner(ChatPlugin):
    command = "owner"
    helper = "Change user level to owner. /owner user"
    room = True
    permission = ability.Permissions.set_owner

    def __call__(self, serv, message):
        user = serv.session.query(models.User).filter_by(name=message).first()
        if not user:
            serv.send_message("Unknown user %s" % with_color(message), to="me")
            return

        if user.level(serv.conn.room) > serv.level(serv.conn.room):
            serv.send_message("Not authorize to owner %s" % with_color(user.fullname(serv.conn.room)), to="me")
            return

        user.set_level(serv.room.id, 10)
        serv.send_message("%s give operator right to %s" % (
            serv.colored_user_repr(serv.room.id),
            with_color(user.fullname(serv.room.id))
        ))


class ChatVoice(ChatPlugin):
    command = "voice"
    helper = "Change user level to voice. /voice user"
    room = True
    permission = ability.Permissions.set_voice

    def __call__(self, serv, message):
        user = serv.session.query(models.User).filter_by(name=message).first()
        if not user:
            serv.send_message("Unknown user %s" % with_color(message), to="me")
            return

        if user.level(serv.conn.room) > serv.level(serv.conn.room):
            serv.send_message("Not authorize to voice %s" % with_color(user.fullname(serv.conn.room)), to="me")
            return

        user.set_level(serv.room.id, 1)
        serv.send_message("%s give voice right to %s" % (
            serv.colored_user_repr(serv.room.id),
            with_color(user.fullname(serv.room.id))
        ))

