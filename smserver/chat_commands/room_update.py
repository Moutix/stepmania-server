""" Chat command for room update """

from smserver import ability
from smserver import models
from smserver import services
from smserver.resources import room_resource
from smserver.chatplugin import ChatPlugin
from smserver.controllers.legacy.enter_room import EnterRoomController

class ChatRoomUpdate(ChatPlugin):
    """ Generic room update command """

    room = True
    permission = ability.Permissions.change_room_settings

    field = None

    def __call__(self, resource, message):
        connection = resource.connection
        setattr(connection.room, self.field, message)

        services.chat.send_message_room(
            room_id=connection.room_id,
            message="Room %s set to '%s' by %s" % (
                self.field,
                message,
                models.User.colored_users_repr(
                    connection.active_users,
                    connection.room_id
                ),
            )
        )

class ChatMaxUsers(ChatRoomUpdate):
    """ /mas_users command. Change the nb max of users in a room """

    command = "max_users"
    helper = "Set nb_max of users (0 to 255)."

    field = "max_users"

    def __call__(self, resource, message):
        try:
            value = int(message)
        except ValueError:
            value = None

        if not value or value < 0 or value > 255:
            return ["Invalid number: Please enter a correct value (0:255)"]

        super().__call__(resource, value)

class ChatMOTD(ChatRoomUpdate):
    """ /motd command. Change the motd in a room """

    command = "motd"
    helper = "Update room MOTD"

    field = "motd"


class ChatDescription(ChatRoomUpdate):
    """ /description command. Change the description in a room """

    command = "description"
    helper = "Update room description"

    field = "description"


class ChatRoomHidden(ChatRoomUpdate):
    """ /hide command. Change the display of a room """

    command = "hide"
    helper = "Show/Hide the room"

    field = "hidden"

    def __call__(self, resource, message):
        super().__call__(resource, not resource.connection.room.hidden)

class ChatRoomFree(ChatRoomUpdate):
    """ /free command. Change the liberty of a room """

    command = "free"
    helper = "Free/Unfree the room"

    field = "free"

    def __call__(self, resource, message):
        super().__call__(resource, not resource.connection.room.free)

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
