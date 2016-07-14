#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
    This module add the class use to handle smpacket.

    All the controllers placed in the controllers folder will be loaded.
    You can also add your own controller in the plugins folder.

    :Example:

    Here's a simple Controller which will send a HelloWorld on every
    PingMessage::

        class ControllerHelloWorld(StepmaniaController):
            command = smpacket.SMClientCommand.NSCPing
            require_login = False

            def handle(self):
                serv.send_message("Hello world", to="me")
"""

from datetime import datetime

from smserver.smutils import smpacket
from smserver import models, ability
from smserver.chathelper import with_color

class StepmaniaController(object):
    """
        Inherit from this class to add an action every time you will see a
        specific packet.

        A new instance of StepmaniaController is instantiate on each incoming
        packet.

        :param server: The main server instance.
        :param conn: The connection from who the packet is comming from
        :param packet: The packet send
        :param session: A session object use to interact with the database
        :type server: smserver.server.StepmaniaServer
        :type conn: smserver.smutils.smconn.StepmaniaConn
        :type packet: smserver.smutils.smpacket.SMPacket
        :type session: sqlalchemy.orm.session.Session
    """

    command = None
    """
        The command to handle in this controller.

        :rtype: smserver.smutils.smpacket.SMClientCommand
    """

    require_login = False
    """
        Specify if the user has to be log in.

        :rtype: bool
    """

    def __init__(self, server, conn, packet, session):
        self.server = server
        self.conn = conn
        self.packet = packet
        self.session = session
        self.log = self.server.log

        self._room = None
        self._users = None
        self._room_users = None
        self._song = None

    @property
    def room(self):
        """
            The room object where the user is.

            Return None if the user is not in a room
        """

        if not self.conn.room:
            return None

        if not self._room:
            self._room = self.session.query(models.Room).get(self.conn.room)

        return self._room

    def song(self):
        """
            Return the song object the last song the user have selected.

            Return None if there is no such song.
        """

        if not self.conn.song:
            return None

        if not self._song:
            self._song = self.session.query(models.Song).get(self.conn.song)

        return self._song

    @property
    def users(self):
        """
            Return the list of connected user's object.
        """

        if not self._users:
            self._users = models.User.get_from_ids(self.conn.users, self.session)

        return self._users

    @property
    def active_users(self):
        """
            Return the list of connected user's object which are still online.
        """

        return [user for user in self.users if user.online]

    @property
    def room_users(self):
        """
            Return the list of user currently in the same room
        """

        if not self._room_users:
            self._room_users = self.session.query(models.User).filter_by(romm_id=self.conn.room)

        return self._room_users

    def user_repr(self, room_id=None):
        """
            A textual representation of the users connected on this connection.

            :param room_id: The ID of the room
            :type room_id: int
            :return: A textual representations of the users name
            :rtype: str
        """

        return "%s" % " & ".join(user.fullname(room_id) for user in self.active_users)

    def colored_user_repr(self, room_id=None):
        """
            A colored textual representation of the users connected on this
            connection. Use it when sending chat message

            :param room_id: The ID of the room
            :type room_id: int
            :return: A colored textual representations of the users name
            :rtype: str
        """

        return "%s" % " & ".join(with_color(user.fullname(room_id)) for user in self.active_users)

    def level(self, room_id=None):
        """
            The maximum level of the users in this connection

            :param room_id: The ID of the room.
            :type room_id: int
            :return: Level of the user
            :rtype: int
        """

        return max(user.level(room_id) for user in self.active_users)

    def can(self, action, room_id=None):
        """
            Return True if this connection can do the specified action

            :param action: The action to do
            :param room_id: The ID of the room where the action take place.
            :type action: smserver.ability.Permissions
            :type room_id: int
            :return: True if the action in authorized
        """

        return ability.Ability.can(action, self.level(room_id))

    def cannot(self, action, room_id=None):
        """
            Return True if this connection cannot do the specified action

            :param action: The action to do
            :param room_id: The ID of the room where the action take place.
            :type action: smserver.ability.Permissions
            :type room_id: int
            :return: True if the action in unauthorized
        """

        return ability.Ability.cannot(action, self.level(room_id))

    def handle(self):
        """
            This method is call on every incoming packet.

            Do all the stuff you need here.
        """
        pass

    def send(self, packet):
        """
            Send the specified packet to the current connection

            :param packet: The packet to send
            :type packet: smserver.smutils.smpacket.SMPacket
            :return: nothing
        """

        self.conn.send(packet)

    def sendall(self, packet):
        """
            Send the specified packet to all the connections on the server

            :param packet: The packet to send
            :type packet: smserver.smutils.smpacket.SMPacket
            :return: nothing
        """

        self.server.sendall(packet)

    def sendroom(self, room, packet):
        """
            Send the specified packet to all the connection in the specified room

            :param room_id: The ID of the room
            :param packet: The packet to send
            :type room_id: int
            :type packet: smserver.smutils.smpacket.SMPacket
            :return: nothing
        """

        self.server.sendroom(room, packet)

    def sendplayers(self, room_id, packet):
        """
            Send the specified packet to all the players in the specified room
            which have send an NSCGSR packet

            :param room_id: The ID of the room
            :param packet: The packet to send
            :type room_id: int
            :type packet: smserver.smutils.smpacket.SMPacket
            :return: nothing
        """

        self.server.sendroom(room_id, song_id, packet)

    def send_message(self, message, to=None, room_id=None):
        """
            Send a chat message

            :param message: The message to send.
            :param to: Send the message to ? (room, all, me). Default to room
            :param room_id: A specific room. Default to the room connection.
            :type message: str
            :type to: str
            :type room_id: int
            :return: nothing
        """

        func = {
            "me": self.send,
            "all": self.sendall,
            "room": self.sendroom
        }.get(to)

        if func == self.sendroom or (not func and self.room) or room_id:
            room = self.session.query(models.Room).get(room_id) if room_id else self.room
            message = "[%s] #%s %s" % (datetime.now().strftime("%X"), with_color(room.name), message)
            packet = smpacket.SMPacketServerNSCCM(message=message)
            self.sendroom(room.id, packet)
            return

        message = "[%s] %s" % (datetime.now().strftime("%X"), message)
        packet = smpacket.SMPacketServerNSCCM(message=message)

        if func:
            func(packet)
            return

        self.server.sendall(packet)

    def send_user_message(self, message, to=None):
        """
            Same as send_message but prepend the user repr to the message

            :param message: The message to send.
            :param to: Send the message to ? (room, all, me). Default to room
            :type message: str
            :type to: str
            :return: nothing
        """

        self.send_message(
            "%s %s" % (
                self.colored_user_repr(self.conn.room),
                message),
            to)

