""" Chat event worker module """

from smserver.chathelper import with_color
from smserver import models
from smserver.smutils.smpacket import smpacket
from smserver.listener.workers import base

class ChatWorker(base.BaseWorker):
    """ Chat worker """

    need_session = True

    def handle(self, data, token=None, *, session=None):
        """ Handle a new incomming chat message """

        target = data.get("target", "")
        message = data.get("message", "")
        source = data.get("source")

        connection = models.Connection.by_token(source, session) if source else None
        if connection:
            message = "%s %s" % (
                models.User.colored_users_repr(
                    connection.active_users,
                    connection.room_id
                ),
                message
            )

        if target.startswith("~"):
            self.send_message_room(
                message=message,
                room=models.Room.by_name(
                    session=session,
                    name=target.split("~", 1)[1],
                )
            )
            return

        self.send_message_token(message, target)

    def send_message_token(self, message, token):
        """ Send a message to a token

            :param str message: Message to send
        """

        packet = smpacket.SMPacketServerNSCCM(
            message=message
        )

        self.server.sendconnection(token, packet)

    def send_message_room(self, message, room):
        """ Send a message to a room

            :param str message: Message to send
            :param room: Room to send the message
            :type room: smserver.models.room.Room
        """
        if not room:
            self.log.warning("Trying to send message to unknown room: %r", message)
            return

        packet = smpacket.SMPacketServerNSCCM(
            message=message
        )
        packet["message"] = "#%s %s" % (with_color(room.name), message)

        self.server.sendroom(room.id, packet)
