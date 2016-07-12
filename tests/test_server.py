#!/usr/bin/env python3
# -*- coding: utf8 -*-

import pytest

from smserver import server, conf, models
from smserver.smutils import smpacket
from smserver.smutils.smconnections import smtcpsocket, websocket

class ClientTestBinary(smtcpsocket.SocketConn):
    def __init__(self, serv, ip, port):
        smtcpsocket.SocketConn.__init__(self, serv, ip, port, None)
        self.packet_send = []

    def send(self, packet):
        self.packet_send.append(packet)
        return packet


class ClientTestJSON(websocket.WebSocketClient):
    def __init__(self, serv, ip, port):
        websocket.WebSocketClient.__init__(self, serv, ip, port, None, None, None)
        self.packet_send = []

    def send(self, packet):
        self.packet_send.append(packet)
        return packet

class ServerTest(server.StepmaniaServer):
    pass

config = conf.Conf("--update_schema")

server_test = ServerTest(config)

client_bin = ClientTestBinary(server_test, "42.42.42.42", 4271)
client_json = ClientTestJSON(server_test, "50.50.50.50", 7272)

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


@pytest.yield_fixture()
def session():
    with server_test.db.session_scope() as sess:
        yield sess


def test_addclient():
    server_test.add_connection(client_bin)
    server_test.add_connection(client_json)

    assert client_bin in server_test.connections
    assert client_json in server_test.connections

def test_hello_binary():
    client_bin._on_data(smpacket.SMPacketClientNSCHello(name="stepmania-binary", version=40).binary)

    assert client_bin.stepmania_name == "stepmania-binary"
    assert client_bin.stepmania_version == 40

    assert smpacket_in(smpacket.SMPacketServerNSCHello, client_bin.packet_send)
    client_bin.packet_send = []

def test_hello_json():
    client_json._on_data(smpacket.SMPacketClientNSCHello(name="stepmania-json", version=41).json)

    assert client_json.stepmania_name == "stepmania-json"
    assert client_json.stepmania_version == 41

    assert smpacket_in(smpacket.SMPacketServerNSCHello, client_json.packet_send)
    client_json.packet_send = []

def test_client_bin_sign_in(session):
    client_bin._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientLogin(username="clientbin-user1", password="test", player_number=0)
    ).binary)

    user = session.query(models.User).filter_by(name="clientbin-user1").first()

    assert user.online is True
    assert user.last_ip == client_bin.ip
    assert user.room is None
    assert user.pos == 0

    assert user.id in client_bin.users

def test_client_json_sign_in(session):
    client_json._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientLogin(username="clientjson-user1", password="test", player_number=0)
    ).json)

    user = session.query(models.User).filter_by(name="clientjson-user1").first()

    assert user.online is True
    assert user.last_ip == client_json.ip
    assert user.room is None
    assert user.pos == 0

    assert user.id in client_json.users

def test_client_bin_sign_in_2(session):
    client_bin._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientLogin(username="clientbin-user2", password="test", player_number=1)
    ).binary)

    user = session.query(models.User).filter_by(name="clientbin-user2").first()

    assert user.online is True
    assert user.last_ip == client_bin.ip
    assert user.room is None
    assert user.pos == 1

    assert user.id in client_bin.users

def test_client_bin_logout_user(session):
    """ Player select only one profile, we disconnect the player 1"""
    client_bin._on_data(smpacket.SMPacketClientNSCSU(player_id=0, nb_players=1, player_name="name").binary)

    user2 = session.query(models.User).filter_by(name="clientbin-user2").first()
    assert user2.online is False

    user1 = session.query(models.User).filter_by(name="clientbin-user1").first()
    assert user1.online is True

def test_client_bin_reconnect_user(session):
    """ Player select only two profile, we reconnect the offline player """
    client_bin._on_data(smpacket.SMPacketClientNSCSU(player_id=0, nb_players=2, player_name="name").binary)

    user2 = session.query(models.User).filter_by(name="clientbin-user2").first()
    assert user2.online is True

    user1 = session.query(models.User).filter_by(name="clientbin-user1").first()
    assert user1.online is True

def test_client_bin_room_creation(session):
    client_bin._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientCreateRoom(
            type=1,
            title="Room client-bin",
            description="test room",
            password="password")
    ).binary)

    room = session.query(models.Room).filter_by(name="Room client-bin").first()
    user1 = session.query(models.User).filter_by(name="clientbin-user1").first()
    user2 = session.query(models.User).filter_by(name="clientbin-user2").first()

    assert client_bin.room == room.id
    assert room.description == "test room"

    assert user1.room == room
    assert user2.room == room

    assert user1.level(room.id) == 10
    assert user2.level(room.id) == 10

def test_json_room_info(session):
    client_json.packet_send = []

    client_json._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientRoomInfo(room="Room client-bin")
    ).json)

    packet = get_smpacket_in(smpacket.SMPacketServerNSSMONL, client_json.packet_send)

    assert packet is not None

    assert isinstance(packet["packet"], smpacket.SMOPacketServerRoomInfo)

    assert packet["packet"]["num_players"] == 2
    assert "clientbin-user1" in packet["packet"]["players"]
    assert "clientbin-user2" in packet["packet"]["players"]

def test_json_fail_create_room_name_already_taken(session):
    client_json._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientCreateRoom(
            type=1,
            title="Room client-bin",
            description="test room",
            password="password")
    ).json)

    assert client_json.room is None

def test_json_fail_enter_room_wrong_password(session):
    client_json._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientEnterRoom(enter=1, room="Room client-bin", password="wrong password")
    ).json)

    assert client_json.room is None

def test_json_enter_room(session):
    client_json._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientEnterRoom(enter=1, room="Room client-bin", password="password")
    ).json)

    room = session.query(models.Room).filter_by(name="Room client-bin").first()
    user = session.query(models.User).filter_by(name="clientjson-user1").first()

    assert client_json.room == room.id
    assert user.room == room
    assert user.level(room.id) == 1


