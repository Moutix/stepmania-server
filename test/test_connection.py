#!/usr/bin/env python3
# -*- coding: utf8 -*-

from test.helper import *

server_test = get_server_test()
client_bin = ClientTestBinary(server_test)
client_json = ClientTestJSON(server_test)

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

