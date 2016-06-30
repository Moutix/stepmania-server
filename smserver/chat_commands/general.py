#!/usr/bin/env python3
# -*- coding: utf8 -*-


from smserver import models
from smserver.chathelper import with_color
from smserver.chatplugin import ChatPlugin


class ChatHelp(ChatPlugin):
    command = "help"
    helper = "Show help"

    def __call__(self, serv, message):
        for command, action in sorted(serv.server.chat_commands.items()):
            if not action.can(serv):
                continue

            serv.send_message("/%s: %s" % (command, action.helper), to="me")

class ChatUserListing(ChatPlugin):
    command = "users"
    helper = "List users"

    def __call__(self, serv, message):
        users = serv.session.query(models.User).filter_by(online=True)
        max_users = serv.server.config.server.get("max_users")
        if serv.room:
            users = users.filter_by(room_id=serv.room.id)
            max_users = serv.room.max_users

        users = users.all()
        serv.send_message("%s/%s players online" % (len(users), max_users), to="me")

        for user in users:
            serv.send_message(
                "%s (in %s)" % (
                    with_color(user.fullname(serv.conn.room)),
                    user.enum_status.name),
                to="me")

