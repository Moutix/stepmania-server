""" Base test class for all the functional test"""

import mock

from smserver import server
from smserver import models
from smserver.smutils.smconnections import websocket
from smserver.smutils.smconnections import smtcpsocket
from smserver.smutils.smpacket import smpacket

from test import utils

class ClientTestBinary(smtcpsocket.SocketConn):
    """ Fake client connection with bin encoding """

    def __init__(self, serv, ip="1.1.1.1", port=4444):
        smtcpsocket.SocketConn.__init__(self, serv, ip, port, None)
        self.packet_send = []
        self._conn = mock.MagicMock()

    def connect_to_serv(self):
        """ Send hello message and add the connection """

        self._serv.add_connection(self)
        self._on_data(smpacket.SMPacketClientNSCHello(name="stepmania-binary", version=40).binary)

    def on_data(self, data):
        """ Received new data"""

        self._on_data(data)

    def send(self, packet):
        self.packet_send.append(packet)
        return packet

class ClientTestJSON(websocket.WebSocketClient):
    """ Fake client connection with JSON encoding """

    def __init__(self, serv, ip="2.2.2.2", port=4444):
        websocket.WebSocketClient.__init__(self, serv, ip, port, None, None, None)
        self.packet_send = []
        self._conn = mock.MagicMock()

    def connect_to_serv(self):
        """ Send hello message and add the connection """

        self._serv.add_connection(self)
        self._on_data(smpacket.SMPacketClientNSCHello(name="stepmania-json", version=40).json)

    def on_data(self, data):
        """ Received new data"""

        self._on_data(data)

    def send(self, packet):
        self.packet_send.append(packet)
        return packet

class ServerTest(server.StepmaniaServer):
    """ Server use for all the functional test """

    def add_bin_connection(self, ip="1.1.1.1", port=4444):
        client = ClientTestBinary(self, ip, port)
        client.connect_to_serv()
        return client

    def add_json_connection(self, ip="2.2.2.2", port=4444):
        client = ClientTestJSON(self, ip, port)
        client.connect_to_serv()
        return client

class FunctionalTest(utils.DBTest):
    """ Base class for all the functional test """

    def setUp(self):
        super().setUp()
        self.server = ServerTest()
        self.client_bin = ClientTestBinary(self.server)
        self.client_json = ClientTestJSON(self.server)

    def tearDown(self):
        self.assertNotLog("ERROR")
        super().tearDown()
        self.client_bin.packet_send = []
        self.client_json.packet_send = []

    @property
    def bin_connection(self):
        """ Return the connection object assiciated with the client_bin"""
        return models.Connection.by_token(self.client_bin.token, self.session)

    @property
    def json_connection(self):
        """ Return the connection object assiciated with the client_json"""

        return models.Connection.by_token(self.client_json.token, self.session)

    def assertJSONSend(self, packet_class):
        """ Assert the json client have send the given packet"""
        list_packet = self.client_json.packet_send

        test = False
        for packet in list_packet:
            test |= isinstance(packet, packet_class)

        self.assertTrue(test, "Packet %s not found in %s" % (packet_class, list_packet))

    def assertBinSend(self, packet_class):
        """ Assert the bin client have send the given packet"""
        list_packet = self.client_bin.packet_send

        test = False
        for packet in list_packet:
            test |= isinstance(packet, packet_class)

        self.assertTrue(test, "Packet %s not found in %s" % (packet_class, list_packet))

    @staticmethod
    def get_smpacket_in(packet_class, list_packet):
        pack = None
        for packet in list_packet:
            if isinstance(packet, packet_class):
                pack = packet

        return pack

class ConnectedFunctionalTest(FunctionalTest):
    """ Functional test with a server and 2 connected client """

    def setUp(self):
        super().setUp()
        self.client_bin = self.server.add_bin_connection()
        self.client_json = self.server.add_json_connection()

class UserFunctionalTest(ConnectedFunctionalTest):
    """ Functional test with a server and 2 connected client """

    def setUp(self):
        super().setUp()
        self.client_bin.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientLogin(
                username="clientbin-user1",
                password="testtest",
                player_number=0
            )
        ).binary)
        self.client_bin.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientLogin(
                username="clientbin-user2",
                password="testtest",
                player_number=1
            )
        ).binary)
        self.client_json.on_data(smpacket.SMPacketClientNSSMONL(
            packet=smpacket.SMOPacketClientLogin(
                username="clientjson-user1",
                password="testtest",
                player_number=0
            )
        ).json)

    @property
    def user_bin1(self):
        """ Return the user 1 attache to the client bin"""
        return self.session.query(models.User).filter_by(name="clientbin-user1").first()

    @property
    def user_bin2(self):
        """ Return the user 1 attache to the client bin"""
        return self.session.query(models.User).filter_by(name="clientbin-user2").first()

    @property
    def user_json1(self):
        """ Return the user 1 attache to the client bin"""
        return self.session.query(models.User).filter_by(name="clientjson-user1").first()
