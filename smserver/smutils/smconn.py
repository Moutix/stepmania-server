""" SMConnection Module.

Base module for handling all type of connection
"""

import datetime
import logging
import uuid

from threading import Lock, Thread

from smserver.smutils import smpacket

class StepmaniaConn(object):
    logger = logging.getLogger('stepmania')
    ENCODING = "binary"
    ALLOWED_PACKET = []

    """ A stepmania connection is represented by a token in the database """

    def __init__(self, serv, ip, port):
        self.mutex = Lock()

        self._serv = serv
        self.ip = ip
        self.port = port

        self.token = uuid.uuid4().hex

        self.users = []
        self.room = None

        self.songs = {}
        self.song = None
        self.songstats = {0: {"data": []}, 1: {"data": []}}

        self.wait_start = False
        self.ingame = False
        self.spectate = False

        self.chat_timestamp = False

        self.last_ping = datetime.datetime.now()
        self.stepmania_version = None
        self.stepmania_name = None

    def run(self):
        """ Start to listen for incomming data """
        for data in self.received_data():
            if data is None:
                break

            self._on_data(data)

        self.close()

    def received_data(self):
        pass

    def _on_data(self, data):
        """ Action to perform on new data """

        packet = smpacket.SMPacket.from_(self.ENCODING, data)
        if not packet:
            self.logger.info("packet %s drop from %s", data, self.ip)
            return None

        self.logger.debug("Packet received from %s: %s", self.ip, packet)

        if self.ALLOWED_PACKET and packet.command not in self.ALLOWED_PACKET:
            self.logger.debug("packet %s ignored from %s", data, self.ip)
            return None

        if packet.command == smpacket.SMClientCommand.NSCPingR:
            self.last_ping = datetime.datetime.now()

        self._serv.on_packet(self, packet)

    def send(self, packet):
        """ How to send a new packet """

        if packet.command == smpacket.SMServerCommand.NSCCM and self.chat_timestamp:
            packet["message"] = "[%s] %s" % (
                datetime.datetime.now().strftime("%X"),
                packet["message"]
            )

        self.logger.debug("packet send to %s: %s", self.ip, packet)
        self._send_data(packet.to_(self.ENCODING))

    def _send_data(self, data):
        pass

    def close(self):
        """ Close the connection """
        self._serv.on_disconnect(self)


class SMThread(Thread):
    logger = logging.getLogger('stepmania')

    def __init__(self, server, ip, port):
        Thread.__init__(self)
        self.daemon = True
        self.server = server
        self.ip = ip
        self.port = port

    def run(self):
        self.logger.info("Successfully close thread: %s", self)

    def stop(self):
        self.logger.debug("Closing thread: %s", self)
