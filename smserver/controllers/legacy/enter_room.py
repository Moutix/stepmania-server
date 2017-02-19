""" Enter room controller module """

from smserver.smutils.smpacket import smpacket
from smserver.smutils.smpacket import smcommand

from smserver.chathelper import with_color
from smserver.stepmania_controller import StepmaniaController
from smserver.resources.room_resource import RoomResource
from smserver import models
from smserver import exceptions

class EnterRoomController(StepmaniaController):
    """ Enter room controller"""

    command = smcommand.SMOClientCommand.ENTERROOM
    require_login = True

    def handle(self):
        room_resource = RoomResource(self.server, self.conn.token, self.session)

        if self.packet["enter"] == 0:
            room_resource.leave()
            self.send(models.Room.smo_list(self.session, self.active_users))

            return

        try:
            room = room_resource.login(self.packet["room"], self.packet["password"])
        except exceptions.Forbidden:
            self.send_message(
                "Unauthorized to enter in the room {name}".format(
                    name=with_color(self.packet["room"])
                )
            )
            return
        except exceptions.Unauthorized:
            self.send_message(
                "The room {name} is full".format(
                    name=with_color(self.packet["room"])
                )
            )
            return

        self.send(smpacket.SMPacketServerNSSMONL(
            packet=room.to_packet()
        ))

        self.send_room_resume(self.server, self.conn, room)

    @staticmethod
    def send_room_resume(server, conn, room):
        """
            Send the room welcome information.

            :param server: Main server
            :param conn: Connection target
            :param room: Room to be resume
            :type server: smserver.server.StepmaniaServer
            :type conn: smserver.smutils.smconn.StepmaniaConn
            :type room: smserver.models.room.Room
        """

        messages = []

        messages.append(
            "Room %s (%s), created at %s" % (
                with_color(room.name),
                room.mode if room.mode else "normal",
                room.created_at
            )
        )

        messages.append(
            "%s/%s players online. Moderators: %s" % (
                room.nb_players,
                room.max_users,
                ", ".join(player.fullname_colored(room.id)
                          for player in room.moderators)
            )
        )

        if room.motd:
            messages.append(room.motd)

        for message in messages:
            server.send_message(message, conn=conn)
