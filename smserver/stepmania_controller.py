#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
    This module add the class use to handle smpacket

    :Example:

    Here's a simple Controller which will send a HelloWorld on every PingMessage

    ``
    ControllerHelloWorld(StepmaniaController):
        command = smpacket.SMClientCommand.NSCPing

        def handle(self):
            serv.send_message("Hello world", to="me")
    ``
"""

from datetime import datetime

from smserver.smutils import smpacket
from smserver import models, ability
from smserver.chathelper import with_color

class StepmaniaController(object):
    """
        Inherit from this class to add an action every time you will see a
        specific packet.

        See the controller as a connection (with 1 or 2 users), this class is
        instantiate on every message with the good command.

        command: The smpacket.SMClientCommand to handle
        require_login: True if the user have to be log in.
    """


    command = None
    require_login = False

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
            self._users = self.server.get_users(self.conn.users, self.session)

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
        """

        return "%s" % " & ".join(user.fullname(room_id) for user in self.active_users)

    def colored_user_repr(self, room_id=None):
        """
            A colored textual representation of the users connected on this
            connection. Use it when sending chat message
        """

        return "%s" % " & ".join(with_color(user.fullname(room_id)) for user in self.active_users)

    def level(self, room_id):
        """
            The maximum level of the users in this connection
        """

        return max(user.level(room_id) for user in self.active_users)

    def can(self, action, room_id=None):
        """
            Return True if this connection can do the specified action
        """

        return ability.Ability.can(action, self.level(room_id))

    def cannot(self, action, room_id=None):
        """
            Return True if this connection cannot do the specified action
        """

        return ability.Ability.cannot(action, self.level(room_id))

    def handle(self):
        """
            This method is call on every incoming packet.

            Do all the stuff you need here
        """
        pass

    def send(self, packet):
        """
            Send the specified packet to the connection
        """

        self.conn.send(packet)

    def sendall(self, packet):
        """
            Send the specified packet to all the connections
        """

        self.server.sendall(packet)

    def sendroom(self, room, packet):
        """
            Send the specified packet to all the connection in the specified room
        """

        self.server.sendroom(room, packet)

    def sendplayers(self, room, song, packet):
        """
            Send the specified packet to all the players in the specified room.
        """

        self.server.sendroom(room, song, packet)

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
        """

        self.send_message(
            "%s %s" % (
                self.colored_user_repr(self.conn.room),
                message),
            to)

