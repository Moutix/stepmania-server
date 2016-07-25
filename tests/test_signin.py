#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smserver import models
from smserver.smutils import smpacket

from helper import *

server_test = get_server_test()
client_bin = server_test.add_bin_connection()
client_json = server_test.add_json_connection()

def test_client_bin_sign_in_one_user(session):
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

def test_client_bin_sign_in_second_user(session):
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

def test_client_json_sign_in_one_user(session):
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

def test_json_login_with_same_user(session):
    """ Player reconnect the same user already logued in (in another pos) """

    client_json._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientLogin(username="clientjson-user1", password="test", player_number=1)
    ).json)

    user = session.query(models.User).filter_by(name="clientjson-user1").first()

    assert user.online is True
    assert user.last_ip == client_json.ip
    assert user.room is None
    assert user.pos == 1

    assert user.id in client_json.users
    assert len(client_json.users) == 1

def test_json_sign_in_second_user(session):
    """ A second user sign in the free pos"""

    client_json._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientLogin(username="clientjson-user2", password="test", player_number=0)
    ).json)

    user = session.query(models.User).filter_by(name="clientjson-user2").first()

    assert user.online is True
    assert user.last_ip == client_json.ip
    assert user.room is None
    assert user.pos == 0

    assert user.id in client_json.users

    assert len(client_json.users) == 2

def test_json_sign_in_third_user(session):
    """ A third user connect in a pos already taken """

    client_json._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientLogin(username="clientjson-user3", password="test", player_number=1)
    ).json)

    user3 = session.query(models.User).filter_by(name="clientjson-user3").first()
    user1 = session.query(models.User).filter_by(name="clientjson-user1").first()

    assert user3.online is True
    assert user3.last_ip == client_json.ip
    assert user3.room is None
    assert user3.pos == 1

    assert user3.id in client_json.users

    assert len(client_json.users) == 3

    assert user1.online is False

