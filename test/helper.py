#!/usr/bin/env python3
# -*- coding: utf8 -*-

import pytest

from smserver import server, conf
from smserver.smutils.smconnections import smtcpsocket, websocket
from smserver.smutils import smpacket


class ClientTestBinary(smtcpsocket.SocketConn):
    def __init__(self, serv, ip="1.1.1.1", port=4444):
        smtcpsocket.SocketConn.__init__(self, serv, ip, port, None)
        self.packet_send = []

    def connect_to_serv(self):
        """ Send hello message and add the connection """

        self._serv.add_connection(self)
        self._on_data(smpacket.SMPacketClientNSCHello(name="stepmania-binary", version=40).binary)

    def send(self, packet):
        self.packet_send.append(packet)
        return packet

class ClientTestJSON(websocket.WebSocketClient):
    def __init__(self, serv, ip="2.2.2.2", port=4444):
        websocket.WebSocketClient.__init__(self, serv, ip, port, None, None, None)
        self.packet_send = []

    def connect_to_serv(self):
        """ Send hello message and add the connection """

        self._serv.add_connection(self)
        self._on_data(smpacket.SMPacketClientNSCHello(name="stepmania-json", version=40).json)

    def send(self, packet):
        self.packet_send.append(packet)
        return packet

class ServerTest(server.StepmaniaServer):
    def add_bin_connection(self, ip="1.1.1.1", port=4444):
        client = ClientTestBinary(self, ip, port)
        client.connect_to_serv()
        return client

    def add_json_connection(self, ip="2.2.2.2", port=4444):
        client = ClientTestJSON(self, ip, port)
        client.connect_to_serv()
        return client

def get_server_test():
    config = conf.Conf("--update_schema", "-c", "")

    return ServerTest(config)

def smpacket_in(packet_class, list_packet):
    for packet in list_packet:
        if isinstance(packet, packet_class):
            return True

    return False

def get_smpacket_in(packet_class, list_packet):
    for packet in list_packet:
        if isinstance(packet, packet_class):
            return packet

    return None

@pytest.fixture(scope="module", autouse=True)
def new_server_test(request):
    server_test = getattr(request.module, "server_test")
    if not server_test:
        server_test = get_server_test()

    server_test._init_database()

    return server_test

@pytest.yield_fixture(scope="function")
def session(request):
    server_test = getattr(request.module, "server_test")

    with server_test.db.session_scope() as sess:
        yield sess

@pytest.fixture()
def clean_connections(request):
    server_test = getattr(request.module, "server_test", None)
    if not server_test:
        return

    for conn in server_test.connections:
        conn.packet_send = []

pytestmark = pytest.mark.usefixtures("clean_connections")

