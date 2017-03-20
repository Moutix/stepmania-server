""" Chat command for room update """

from smserver import ability
from smserver import models
from smserver.resources import room_resource
from smserver.chatplugin import ChatPlugin
from smserver.controllers.legacy.enter_room import EnterRoomController

class ChatMaxUsers(ChatPlugin):
    """ /mas_users command. Change the nb max of users in a room """

    command = "max_users"
    helper = "Set nb_max of users (0 to 255)."
    room = True
    permission = ability.Permissions.change_room_settings

    def __call__(self, resource, message):
        try:
            value = int(message)
        except ValueError:
            value = None

        if not value or value < 0 or value > 255:
            return ["Invalid number: Please enter a correct value (0:255)"]

        resource.connection.room.max_users = value
        resource.send("Room max_users set to: %s" % message)


class ChatMOTD(ChatPlugin):
    """ /motd command. Change the motd in a room """

    command = "motd"
    helper = "Update room MOTD"
    room = True
    permission = ability.Permissions.change_room_settings

    def __call__(self, resource, message):
        resource.connection.room.motd = message
        resource.send("Room MOTD set to: %s" % message)


class ChatDescription(ChatPlugin):
    """ /description command. Change the description in a room """

    command = "description"
    helper = "Update room description"
    room = True
    permission = ability.Permissions.change_room_settings

    def __call__(self, resource, message):
        resource.connection.room.description = message
        resource.send("Room description set to: %s" % message)


class ChatRoomHidden(ChatPlugin):
    """ /hide command. Change the display of a room """

    command = "hide"
    helper = "Show/Hide the room"
    room = True
    permission = ability.Permissions.change_room_settings

    def __call__(self, resource, message):
        room = resource.connection.room

        room.hidden = not room.hidden

        resource.send({
            True: "The room is no more visible",
            False: "The room is no more hidden"
        }[room.hidden])


class ChatRoomFree(ChatPlugin):
    """ /free command. Change the liberty of a room """

    command = "free"
    helper = "Free/Unfree the room"
    room = True
    permission = ability.Permissions.change_room_settings

    def __call__(self, resource, message):
        room = resource.connection.room

        room.free = not room.free

        resource.send({
            True: "The room is free",
            False: "The room is no more free"
        }[room.free])


class ChatSpectate(ChatPlugin):
    """ /spectate command. Change the liberty of a room"""

    command = "spectate"
    helper = "Spectator mode"
    room = True

    # FIXME: We don't have to change the connection object here
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

    # FIXME: We don't have to call any controller here
    def __call__(self, serv, message):
        EnterRoomController.send_room_resume(serv.server, serv.conn, serv.room)


class ChatDeleteRoom(ChatPlugin):
    """ /delete command. Delete the current room """

    command = "delete"
    helper = "Delete the current room"
    room = True
    permission = ability.Permissions.delete_room

    def __call__(self, resource, message):
        connection = resource.connection

        resource.send("!! %s delete this room !!" % (
            models.User.colored_users_repr(connection.active_users)
        ))

        room_resource.RoomResource(
            self.server,
            connection=connection
        ).delete(connection.room_id)


class ChatLeaveRoom(ChatPlugin):
    """ /leave command. Leave the current room """

    command = "leave"
    helper = "Leave the current room"
    room = True

    def __call__(self, resource, message):
        connection = resource.connection

        room_resource.RoomResource(
            self.server,
            connection=connection
        ).leave()
