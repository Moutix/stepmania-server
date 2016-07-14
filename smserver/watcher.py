#!/usr/bin/env python3
# -*- coding: utf8 -*-

from threading import Thread, Lock
import time
import datetime
import itertools
import socket

from smserver import models
from smserver.smutils import smpacket
from smserver.controllers.game_start_request import StartGameRequestController

class PeriodicMethods(object):
    """ Decorator to indicate the periodicity of a methods """

    def __init__(self):
        self.functions = []

    def __call__(self, period=1):
        def handler(func):
            self.functions.append((func, period))
            def wrapper(self, *opts):
                func(self, *opts)

            return wrapper

        return handler

periodicmethod = PeriodicMethods()

class StepmaniaWatcher(Thread):
    """ Secondary thread, hold by the main server.
    Call periodically each function with a 'periodicmethod decorator' """

    UDP_PORT = 8765
    UDP_IP = "255.255.255.255"

    def __init__(self, server):
        Thread.__init__(self)

        self.server = server
        self.fps = self.server.config.server.get("fps", 1)
        self.mutex = Lock()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def force_run(self):
        with self.server.db.session_scope() as session:
            for func, _ in periodicmethod.functions:
                func(self, session)

                session.commit()

    def run(self):
        self.server.log.debug("Watcher start")
        func_map = {func: 0 for func, _ in periodicmethod.functions}

        while True:
            with self.server.db.session_scope() as session:
                for func, period in periodicmethod.functions:
                    func_map[func] += 1
                    if func_map[func] < period:
                        continue

                    func(self, session)

                    func_map[func] = 0

                    session.commit()

            time.sleep(self.fps)

    @periodicmethod(5)
    def send_udp(self, session):
        packet = smpacket.SMPacketServerNSCFormatted(
            server_name=self.server.config.server["name"],
            server_port=self.server.config.server["port"],
            nb_players=models.User.nb_onlines(session)
        )

        self._sock.sendto(packet.binary, (self.UDP_IP, self.UDP_PORT))

    @periodicmethod(1)
    def send_ping(self, session):
        self.server.sendall(smpacket.SMPacketServerNSCPing())

    @periodicmethod(2)
    def check_end_game(self, session):
        for room in session.query(models.Room).filter_by(ingame=True):
            if self.room_still_in_game(room):
                continue

            self.server.log.info("Room %s finish is last song: %s" % (room.name, room.active_song_id))
            room.status = 1
            room.ingame = False

            game = room.last_game
            game.end_at = datetime.datetime.now()
            game.active = False
            self.server.sendroom(room.id, game.scoreboard_packet)

    def room_still_in_game(self, room):
        for conn in self.server.room_connections(room.id):
            if conn.ingame is True:
                return True

        return False

    @periodicmethod(1)
    def scoreboard_update(self, session):
        for room in session.query(models.Room).filter_by(ingame=True):
            self.send_scoreboard(room, session)

    def send_scoreboard(self, room, session):
        scores = []
        for conn in self.server.room_connections(room.id):
            with conn.mutex:
                for user in models.User.get_from_ids(conn.users, session):
                    if not user.online:
                        continue

                    if user.pos not in conn.songstats:
                        continue

                    stat = conn.songstats[user.pos].get("data")

                    if not stat:
                        continue

                    scores.append({
                        "user": user,
                        "combo": stat[-1].get("combo"),
                        "grade": stat[-1].get("grade"),
                        "score": stat[-1].get("score")
                    })

        for songstat in room.last_game.song_stats:
            if not songstat.user.online:
                continue

            scores.append({
                "user": songstat.user,
                "combo": songstat.max_combo,
                "grade": songstat.grade,
                "score": songstat.score,
            })

        scores.sort(key=lambda x: x['score'], reverse=True)

        packet = smpacket.SMPacketServerNSCGSU(
            nb_players=len(scores),
        )

        packet["section"] = 0
        packet["options"] = [models.User.user_index(score["user"].id, room.id, session) for score in scores]
        self.server.sendroom(room.id, packet)

        packet["section"] = 1
        packet["options"] = [score["combo"] for score in scores]
        self.server.sendroom(room.id, packet)

        packet["section"] = 2
        packet["options"] = [score["grade"] for score in scores]
        self.server.sendroom(room.id, packet)

    @periodicmethod(1)
    def send_game_start(self, session):
        conn_in_room = itertools.filterfalse(lambda x: x.room is None, self.server.connections)

        conns = sorted(conn_in_room, key=lambda x: x.room)
        for room_id, room_conns in itertools.groupby(conns, key=lambda x: x.room):
            if not room_id:
                continue

            self.check_song_start(session, room_id, room_conns)

    def check_song_start(self, session, room_id, room_conns):
        room = session.query(models.Room).get(room_id)
        song = room.active_song

        if room.status != 2:
            return

        everybody_waiting = True
        wait_since = None
        for conn in room_conns:
            with conn.mutex:
                if not conn.wait_start:
                    everybody_waiting = False
                    continue

                if conn.songs.get(song.id) is False:
                    continue

                wait_since = conn.songstats.get("start_at", wait_since)

        if everybody_waiting or (
                wait_since and
                datetime.datetime.now() - wait_since < datetime.timedelta(seconds=3)):

            StartGameRequestController.launch_song(room, song, self.server)

