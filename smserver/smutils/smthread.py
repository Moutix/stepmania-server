""" SMThread module

This module handle the orchestration between all the servers and connections.
"""


import sys
from threading import Lock
from collections import defaultdict

from smserver import logger
from smserver.smutils.smconnections import smtcpsocket, udpsocket
if sys.version_info[1] > 2:
    from smserver.smutils.smconnections import asynctcpserver, websocket

class StepmaniaServer(object):
    """ Main class of the server """

    _logger = logger.get_logger()

    SERVER_TYPE = {
        "classic": smtcpsocket.SocketServer,
        "udp": udpsocket.UDPServer,
        "async": asynctcpserver.AsyncSocketServer,
        "websocket": websocket.WebSocketServer if sys.version_info[1] > 2 else None
    }

    def __init__(self, servers):
        self.mutex = Lock()
        self._connections = {}

        #FIXME: Handle this in a redis server if available
        self._room_connections = defaultdict(set)

        self._servers = []
        for ip, port, server_type in servers:
            self._servers.append(self.SERVER_TYPE[server_type](self, ip, port))

    def is_alive(self):
        """ Check if all the thread are still alive """

        for server in self._servers:
            if not server.is_alive():
                return False

        return True

    def start(self):
        """ Start all the server in the list of servers """

        for server in self._servers:
            server.start()

        for server in self._servers:
            server.join()

    @property
    def connections(self):
        """ List al the connections of this server """
        with self.mutex:
            return self._connections.values()

    def add_connection(self, conn):
        """ Add a new connection to the server """
        self._logger.info("New connection: %s on port %s", conn.ip, conn.port)

        with self.mutex:
            self._connections[conn.token] = conn

    def add_to_room(self, token, room_id):
        """ Add a connection to a new room """

        with self.mutex:
            if token not in self._connections:
                self._logger.error("Tring to add delete connection %s in a room %s", token, room_id)
                return None

            conn = self._connections[token]
            conn.room = room_id

            self._room_connections[room_id].add(token)

    def del_from_room(self, token, room_id=None):
        """ remove a token from a room """

        with self.mutex:
            if token not in self._connections:
                self._logger.error("Tring to add delete connection %s in a room %s", token, room_id)
                return None

            conn = self._connections[token]
            if not room_id:
                room_id = conn.room

            if token not in self._room_connections[room_id]:
                return

            self._room_connections[room_id].remove(token)
            conn.room = None

    def find_connection(self, token):
        """ Find the connection where a specific user is """

        with self.mutex:
            return self._connections.get(token)

    def room_connections(self, room_id):
        """ Iterator of all the connections in a given room """

        with self.mutex:
            for token in self._room_connections.get(room_id, ()):
                if token not in self._connections:
                    continue

                yield self._connections[token]

    def player_connections(self, room_id):
        """ Iterator of all the connection's player (not spectator) """

        for conn in self.room_connections(room_id):
            if conn.spectate is True:
                continue

            yield conn

    def ingame_connections(self, room_id):
        """ Iterator of all the connections in a given room which have send a NSCGSR packet """

        for conn in self.room_connections(room_id):
            if not conn.songstats.get("start_at"):
                continue

            yield conn

    def sendconnection(self, token, packet):
        """ Send a packet to the given connection token """

        conn = self.find_connection(token)
        if conn:
            conn.send(packet)

    def sendall(self, packet):
        """
            Send a packet to all the connections in the server

            :param packet: The packet to send
            :type packet: smserver.smutils.smpacket.SMPacket
        """

        for conn in self.connections:
            conn.send(packet)

    def sendroom(self, room_id, packet):
        """
            Send a packet to all the connections in the room

            :param int room_id: Room_id where to send the packet
            :param packet: The packet to send
            :type packet: smserver.smutils.smpacket.SMPacket
        """

        for conn in self.room_connections(room_id):
            conn.send(packet)

    def sendingame(self, room_id, packet):
        """
            Send a packet to all the connections currently playing in the room

            :param int room_id: Room_id where to send the packet
            :param packet: The packet to send
            :type packet: smserver.smutils.smpacket.SMPacket
        """

        for conn in self.ingame_connections(room_id):
            conn.send(packet)

    def sendplayers(self, room_id, packet):
        """
            Send a packet to all the player's connections in the room

            (not to spectator player)

            :param int room_id: Room_id where to send the packet
            :param packet: The packet to send
            :type packet: smserver.smutils.smpacket.SMPacket
        """

        for conn in self.player_connections(room_id):
            conn.send(packet)

    def on_disconnect(self, conn):
        """ Remove a connection from the list of connections """

        with self.mutex:
            self._connections.pop(conn.token, None)
            if conn.token in self._connections.get(conn.room, ()):
                self._connections[conn.room].remove(conn.token)

    def on_packet(self, serv, packet):
        """ Action to perform on each new packet """
