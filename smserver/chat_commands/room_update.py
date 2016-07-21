#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver import ability
from smserver.chatplugin import ChatPlugin
from smserver.controllers.enter_room import EnterRoomController

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


class ChatDescription(ChatPlugin):
    command = "description"
    helper = "Update room description"
    room = True
    permission = ability.Permissions.change_room_settings

    def __call__(self, serv, message):
        serv.room.description = message
        serv.session.commit()
        serv.send_message("Room description set to: %s" % message)


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


class ChatRoomFree(ChatPlugin):
    command = "free"
    helper = "Free/Unfree the room"
    room = True
    permission = ability.Permissions.change_room_settings

    def __call__(self, serv, message):
        if serv.room.free:
            serv.room.free = False
            msg = "The room is no more free"
        else:
            serv.room.free = True
            msg = "The room is free"

        serv.session.commit()
        serv.send_message(msg)


class ChatSpectate(ChatPlugin):
    command = "spectate"
    helper = "Spectator mode"
    room = True

    def __call__(self, serv, message):
        if serv.conn.spectate:
            msg = "You are no more in spectator mode"
            for user in serv.active_users:
                user.status = 1

            serv.conn.spectate = False
        else:
            msg = "You are now in spectator mode"
            serv.conn.spectate = True
            for user in serv.active_users:
                user.status = 0

        serv.send_message(msg)
        serv.server.send_user_list(serv.room)


class ChatRoomInfo(ChatPlugin):
    command = "info"
    helper = "Room resume"
    room = True

    def __call__(self, serv, message):
        EnterRoomController.send_room_resume(serv.server, serv.conn, serv.room)


class ChatDeleteRoom(ChatPlugin):
    command = "delete"
    helper = "Delete the current room"
    room = True
    permission = ability.Permissions.delete_room

    def __call__(self, serv, message):
        serv.send_message("!! %s delete this room !!" % serv.colored_user_repr(serv.conn.room))

        room = serv.room

        for conn in serv.server.room_connections(serv.conn.room):
            serv.server.leave_room(room, conn=conn)

        serv.session.delete(room)


class ChatLeaveRoom(ChatPlugin):
    command = "leave"
    helper = "Leave the current room"
    room = True

    def __call__(self, serv, message):
        serv.server.leave_room(serv.room, conn=serv.conn)

