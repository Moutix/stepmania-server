#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver import models, stepmania_controller
from smserver.smutils import smpacket

from test.helper import *

server_test = get_server_test()
client_bin = server_test.add_bin_connection()
client_json = server_test.add_json_connection()


# login 2 users for client_bin and 1 user for client_json
def test_login(session):
    client_bin._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientLogin(username="clientbin-user1", password="test", player_number=0)
    ).binary)
    client_bin._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientLogin(username="clientbin-user2", password="test", player_number=1)
    ).binary)
    client_json._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientLogin(username="clientjson-user1", password="test", player_number=0)
    ).json)

    user = session.query(models.User).filter_by(name="clientbin-user1").first()
    assert user.online is True
    assert user.last_ip == client_bin.ip
    assert user.room is None
    assert user.pos == 0

    assert user.id in client_bin.users

def test_client_bin_room_creation(session):
    """ First room creation """

    ctrl = stepmania_controller.StepmaniaController(server_test, client_bin, None, session)
    print(ctrl.active_users)

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

