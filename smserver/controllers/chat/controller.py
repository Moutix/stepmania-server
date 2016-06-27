#!/usr/bin/env python3
# -*- coding: utf8 -*-

import re

from smserver.smutils import smpacket
from smserver.stepmania_controller import StepmaniaController
from smserver import models, ability
from smserver.chathelper import with_color

class ChatPlugin(object):
    helper = ""
    permission = None
    room = False

    def can(self, serv):
        if self.room and not serv.room:
            return False

        if self.permission and serv.cannot(self.permission, serv.conn.room):
            return False

        return True


class ChatHelp(ChatPlugin):
    helper = "Show help"

    def __call__(self, serv, message):
        for command, action in sorted(serv.commands.items()):
            if not action.can(serv):
                continue

            serv.send_message("/%s: %s" % (command, action.helper), to="me")

class ChatUserListing(ChatPlugin):
    helper = "List users"

    def __call__(self, serv, message):
        users = serv.session.query(models.User).filter_by(online=True)
        if serv.room:
            users = users.filter_by(room_id=serv.room.id)

        users = users.all()

        for user in users:
            serv.send_message(
                "%s (in %s)" % (
                    with_color(user.fullname(serv.conn.room)),
                    user.enum_status.name),
                to="me")


class ChatMOTD(ChatPlugin):
    helper = "Update room MOTD"
    room = True
    permission = ability.Permissions.change_room_motd

    def __call__(self, serv, message):
        serv.room.motd = message
        serv.session.commit()
        serv.send_message("Room MOTD set to: %s" % message)


class ChatOP(ChatPlugin):
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


class ChatBan(ChatPlugin):
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
        serv.server.send_user_list(serv.session, serv.room.id)


class ChatUnBan(ChatPlugin):
    helper = "UnBan a user. /unban user"
    permission = ability.Permissions.unban_user

    def __call__(self, serv, message):
        user = serv.session.query(models.User).filter_by(name=message).first()
        if not user:
            serv.send_message("Unknown user %s" % with_color(message), to="me")
            return

        models.Ban.unban(serv.session, user_id=user.id, room_id=serv.conn.room)
        serv.send_message("User %s has been unban from this room" % with_color(user.fullname(serv.conn.room)))


class ChatController(StepmaniaController):
    command = smpacket.SMClientCommand.NSCCM
    require_login = True

    commands = {
        "help": ChatHelp(),
        "users": ChatUserListing(),
        "motd": ChatMOTD(),
        "ban": ChatBan(),
        "unban": ChatUnBan(),
        "op": ChatOP(),
        "owner": ChatOwner(),
        "voice": ChatVoice()
    }

    def handle(self):
        message = self.packet["message"]

        key, value = self._parse_message(message)

        if not key:
            self.send_user_message(message)
            return

        if key not in self.commands:
            self.send_message("%s: Unknown command. /help for available commands" % key, to="me")
            return

        if not self.commands[key].can(self):
            self.send_message("%s: Unauthorized action." % key, to="me")
            return

        self.commands[key](self, value)

    @staticmethod
    def _parse_message(message, sufix=r"/"):
        m = re.search(r'^' + sufix + r'(\S+)\s*(.*)$', message)
        if m:
            key = m.group(1).lower()
            value = m.group(2)
        else:
            key = None
            value = None

        return key, value

