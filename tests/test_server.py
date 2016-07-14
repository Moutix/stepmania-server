#!/usr/bin/env python3
# -*- coding: utf8 -*-

import pytest

from smserver import server, conf, models, stepmania_controller
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

config = conf.Conf("--update_schema", "-c", "")

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

@pytest.fixture()
def clean_connections():
    for conn in server_test.connections:
        conn.packet_send = []

pytestmark = pytest.mark.usefixtures("clean_connections")

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
    """ First time login for clientbin-user1, the user is created """

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
    """ First time login for clientjson-user1, the user is created """

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
    """ First time login for clientbin-user2, the user is created """

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
    """ First room creation """

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
    """ Display room information in room selection """

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
    """ Json client create a room that already exist """

    client_json._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientCreateRoom(
            type=1,
            title="Room client-bin",
            description="test room",
            password="password")
    ).json)

    assert client_json.room is None

def test_json_fail_enter_room_wrong_password(session):
    """ Json client try to enter in a room with the wrong password """

    client_json._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientEnterRoom(enter=1, room="Room client-bin", password="wrong password")
    ).json)

    assert client_json.room is None

def test_json_enter_room(session):
    """ Json client enter in the client-bin room """

    client_json._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientEnterRoom(enter=1, room="Room client-bin", password="password")
    ).json)

    room = session.query(models.Room).filter_by(name="Room client-bin").first()
    user = session.query(models.User).filter_by(name="clientjson-user1").first()

    assert client_json.room == room.id
    assert user.room == room
    assert user.level(room.id) == 1

def test_client_json_room_creation(session):
    """ Json client create a new room, and exit the client-bin room """

    client_json._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientCreateRoom(
            type=1,
            title="Room client-json",
            description="test room",
            password="password")
    ).json)

    room = session.query(models.Room).filter_by(name="Room client-json").first()
    user = session.query(models.User).filter_by(name="clientjson-user1").first()

    assert client_json.room == room.id
    assert room.description == "test room"

    assert user.room == room

    assert user.level(room.id) == 10

def test_bin_enter_room(session):
    """ Bin Client enter in json room and exit the other """

    client_bin._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientEnterRoom(enter=1, room="Room client-json", password="password")
    ).binary)

    room = session.query(models.Room).filter_by(name="Room client-json").first()
    user1 = session.query(models.User).filter_by(name="clientbin-user1").first()
    user2 = session.query(models.User).filter_by(name="clientbin-user2").first()

    assert client_bin.room == room.id

    assert user1.room == room
    assert user2.room == room

    assert user1.level(room.id) == 1
    assert user2.level(room.id) == 1

def test_bin_select_song_1(session):
    """ First time song selection, ask if everybody have the song """

    packet = smpacket.SMPacketClientNSCRSG(
        usage=2,
        song_title="Title",
        song_artist="Artist",
    )
    client_bin._on_data(packet.binary)

    controller = stepmania_controller.StepmaniaController(
        server_test, client_bin, packet, session)

    song = session.query(models.Song).filter_by(
        title="Title",
        artist="Artist",
        subtitle=""
    ).first()

    assert song is not None

    assert controller.room.status != 2
    assert controller.conn.song == song.id
    assert controller.conn.ingame is False
    assert get_smpacket_in(smpacket.SMPacketServerNSCRSG, client_bin.packet_send)["usage"] in (0, 1)
    assert get_smpacket_in(smpacket.SMPacketServerNSCRSG, client_json.packet_send)["usage"] in (0, 1)

def test_bin_select_song_2(session):
    packet = smpacket.SMPacketClientNSCRSG(
        usage=2,
        song_title="Title",
        song_artist="Artist",
    )
    client_bin._on_data(packet.binary)

    controller = stepmania_controller.StepmaniaController(
        server_test, client_bin, packet, session)

    song = session.query(models.Song).filter_by(
        title="Title",
        artist="Artist",
        subtitle=""
    ).first()

    assert song is not None

    assert client_bin.wait_start is False
    assert client_json.wait_start is False

    assert controller.room.status == 2
    assert controller.room.active_song == song
    assert get_smpacket_in(smpacket.SMPacketServerNSCRSG, client_bin.packet_send)["usage"] in (2, 3)
    assert get_smpacket_in(smpacket.SMPacketServerNSCRSG, client_json.packet_send)["usage"] in (2, 3)

def test_watcher_game_start(session):
    """
        Watcher run all the script we don't start the song since no NSCGSR
        packet has been sent
    """

    server_test.watcher.force_run()

    assert not smpacket_in(smpacket.SMPacketServerNSCGSR, client_bin.packet_send)

def test_client_bin_game_start_request(session):
    """
        Client-bin send a game start request, wait for client-json
    """

    packet = smpacket.SMPacketClientNSCGSR(
        first_player_feet=8,
        second_player_feet=9,
        first_player_difficulty=3,
        second_player_difficulty=4,
        start_position=0,
        song_title="Title",
        song_artist="Artist",
    )

    client_bin._on_data(packet.binary)

    assert client_bin.wait_start is True
    assert client_bin.ingame is False

def test_client_json_game_start_request(session):
    """
        Client-json send a game start request, start the game
    """

    packet = smpacket.SMPacketClientNSCGSR(
        first_player_feet=5,
        first_player_difficulty=2,
        start_position=0,
        song_title="Title",
        song_artist="Artist",
    )

    client_json._on_data(packet.json)

    assert client_bin.wait_start is False
    assert client_json.wait_start is False
    assert client_bin.ingame is True
    assert client_json.ingame is True

