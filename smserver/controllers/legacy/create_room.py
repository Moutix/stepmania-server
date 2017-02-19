""" Create room controller module """

from smserver.smutils.smpacket import smpacket
from smserver.smutils.smpacket import smcommand

from smserver.chathelper import with_color

from smserver.stepmania_controller import StepmaniaController
from smserver.controllers.legacy import enter_room
from smserver.resources.room_resource import RoomResource
from smserver import exceptions


class CreateRoomController(StepmaniaController):
    """ Create Room controller"""

    command = smcommand.SMOClientCommand.CREATEROOM
    require_login = True

    def handle(self):
        room_resource = RoomResource(self.server, self.conn.token, self.session)

        try:
            room = room_resource.create(
                name=self.packet["title"],
                password=self.packet["password"],
                description=self.packet["description"],
                type_=1
            )
        except exceptions.Forbidden:
            self.send_message(
                "Unauthorized to create the room {name}".format(
                    name=with_color(self.packet["title"])
                )
            )
            return
        except exceptions.ValidationError:
            self.send_message(
                "The room {name} already exist!".format(
                    name=with_color(self.packet["title"])
                )
            )
            return

        room_resource.enter(room)

        self.send(smpacket.SMPacketServerNSSMONL(
            packet=room.to_packet()
        ))

        enter_room.EnterRoomController.send_room_resume(self.server, self.conn, room)
        self.send_message(
            "Welcome to your new room! Type /help for options", to="me"
        )
