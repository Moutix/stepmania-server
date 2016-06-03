#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os

import random

import datetime

from smserver import server, conf
from smserver.smutils import smpacket
from smserver.smutils.smthread import StepmaniaThread

class ClientTest(StepmaniaThread):
    def send(self, packet):
        self._serv.log.debug("%s (%s) send: %s" % (self.ip, self.users, packet))
        print(packet.binary)
        return packet.binary

class ServerTest(server.StepmaniaServer):
    pass


def with_benchmark(func):
    def wrapper(self, *opt):
        start = datetime.datetime.now()
        nb_times = 1000
        for _ in range(1, nb_times):
            func(self, *opt)
        total_time = datetime.datetime.now() - start

        fps = nb_times/(total_time.seconds + (total_time.microseconds/1000000))
        print("Function %s executed %s times in %s s: %s p/s (1packet -> %s ms)" % (
            func.__name__, nb_times, total_time, fps, (1/fps*1000)
            ))
    return wrapper

@with_benchmark
def benchmark_binary(client, packet):
    client._on_data(packet)

def main():
    if "stepmania_test.db" in os.listdir():
        os.remove("stepmania_test.db")
    config = conf.Conf("-c", "conf_test.yml")

    server_test = ServerTest(config)
    server_test.watcher.start()

    client1 = ClientTest(server_test, None, "42.42.42.42", random.randint(4000, 5000))
    client2 = ClientTest(server_test, None, "50.50.50.50", random.randint(4000, 5000))
    server_test.connections.extend([client1, client2])


    client1._on_data(smpacket.SMPacketClientNSCHello(name="stepmania", version=42).binary)
    client2._on_data(smpacket.SMPacketClientNSCHello(name="stepmania", version=45).binary)

    client1._on_data(smpacket.SMPacketClientNSCSU(player_id=0, nb_players=1, player_name="test").binary)

    client1._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientLogin(username="client1-user1", password="test", player_number=0)
        ).binary)

    client1._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientLogin(username="client1-user2", password="test", player_number=1)
        ).binary)

    client1._on_data(smpacket.SMPacketClientNSCSU(player_id=1, nb_players=1, player_name="machin").binary)
    client1._on_data(smpacket.SMPacketClientNSCSU(player_id=1, nb_players=2, player_name="machin").binary)
    client1._on_data(smpacket.SMPacketClientNSCSU(player_id=0, nb_players=1, player_name="machin").binary)


    client2._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientLogin(username="client2-user", password="test")
        ).binary)

    client1._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientCreateRoom(type=1, title="Room client1", description="Room de test", password="aaa")
        ).binary)

    client2._on_data(smpacket.SMPacketClientNSSMONL(
        packet=smpacket.SMOPacketClientRoomInfo(room="Room client1")
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
    client2._on_data(smpacket.SMPacketClientNSCCM(message="/help").binary)
    client2._on_data(smpacket.SMPacketClientNSCCM(message="/users").binary)

    client1._on_data(smpacket.SMPacketClientNSCGSR(song_title="test_song").binary)

    packet = smpacket.SMPacketClientNSCGSU(step_id=7).binary
    print("Becnhmark: %s" % packet)
    benchmark_binary(client1, packet)

    client1._on_data(smpacket.SMPacketClientNSCGON().binary)

if __name__ == "__main__":
    main()


