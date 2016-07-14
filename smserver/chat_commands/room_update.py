#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver import ability
from smserver.chatplugin import ChatPlugin

class ChatMaxUsers(ChatPlugin):
    command = "maxusers"
    helper = "Set nb_max of users (0 to 255)."
    room = True
    permission = ability.Permissions.change_room_settings

    def __call__(self, serv, message):
        try:
            value = int(message)
        except ValueError:
            value = None

        if not value or value < 0 or value > 255:
            serv.send_message("Please enter a correct value (0:255)", to="me")
            return

        serv.room.max_users = value
        serv.session.commit()
        serv.send_message("Room max_users set to: %s" % message)


class ChatMOTD(ChatPlugin):
    command = "motd"
    helper = "Update room MOTD"
    room = True
    permission = ability.Permissions.change_room_settings

    def __call__(self, serv, message):
        serv.room.motd = message
        serv.session.commit()
        serv.send_message("Room MOTD set to: %s" % message)

class ChatRoomHidden(ChatPlugin):
    command = "hide"
    helper = "Show/Hide the room"
    room = True
    permission = ability.Permissions.change_room_settings

    def __call__(self, serv, message):
        if serv.room.hidden:
            serv.room.hidden = False
            msg = "The room is no more hidden"
        else:
            serv.room.hidden = True
            msg = "The room is no more visible"

        serv.session.commit()
        serv.send_message(msg)

