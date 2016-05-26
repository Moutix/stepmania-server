#!/usr/bin/env python3
# -*- coding: utf8 -*-

import sys
import os

import server
import conf
import random

from smutils import smpacket, smserver

class ClientTest(smserver.StepmaniaThread):
    def send(self, packet):
        self._serv.log.debug("%s (%s) send: %s" % (self.ip, self.users, packet))
        print(packet.binary)
        return packet.binary


class ServerTest(server.StepmaniaServer):
    pass

def main():
    if "stepmania_test.db" in os.listdir():
        os.remove("stepmania_test.db")
    config = conf.Conf("-c", "conf_test.yml")

    server_test = ServerTest(config)

    client1 = ClientTest(server_test, None, "42.42.42.42", random.randint(4000, 5000))
    client2 = ClientTest(server_test, None, "50.50.50.50", random.randint(4000, 5000))
    server_test.connections.extend([client1, client2])


    client1._on_data(smpacket.SMPacketClientNSCHello(name="stepmania", version=42).binary)
    client2._on_data(smpacket.SMPacketClientNSCHello(name="stepmania", version=45).binary)

    client1._on_data(smpacket.SMPacketClientNSCSU(player_id=0, nb_players=1, player_name="test").binary)

    client1._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientLogin(username="client1-user1", password="test")
        ).binary)

    client1._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientLogin(username="client1-user2", password="test")
        ).binary)

    client1._on_data(smpacket.SMPacketClientNSCSU(player_id=1, nb_players=1, player_name="machin").binary)
    client1._on_data(smpacket.SMPacketClientNSCSU(player_id=1, nb_players=2, player_name="machin").binary)


    client2._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientLogin(username="client2-user", password="test")
        ).binary)

    client1._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientCreateRoom(type=1, title="Room client1", description="Room de test", password="aaa")
        ).binary)

    client2._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientEnterRoom(enter=1, room="Room client1", password="pas aaa")
        ).binary)

    client2._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientEnterRoom(enter=1, room="Room client1", password="aaa")
        ).binary)


    client1._on_data(smpacket.SMPacketClientNSCRSG(usage=2, song_title="title", song_subtitle="subtitle", song_artist="artist").binary)

    client1._on_data(smpacket.SMPacketClientNSCCM(message="aaa").binary)
    client2._on_data(smpacket.SMPacketClientNSCCM(message="aaa").binary)

if __name__ == "__main__":
    main()


