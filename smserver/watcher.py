#!/usr/bin/env python3
# -*- coding: utf8 -*-

from threading import Thread, Lock
import time
import datetime

from smserver import models
from smserver.smutils import smpacket
from smserver.controllers.game_start_request.controller import StartGameRequestController

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

    def __init__(self, server):
        Thread.__init__(self)

        self.server = server
        self.fps = self.server.config.server.get("fps", 1)
        self.mutex = Lock()

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

    @periodicmethod(1)
    def send_ping(self, session):
        self.server.sendall(smpacket.SMPacketServerNSCPing())

    @periodicmethod(2)
    def check_end_game(self, session):
        for room in session.query(models.Room).filter_by(status=2):
            if self.room_still_in_game(room, session):
                continue

            self.server.log.info("Room %s finish is last song: %s" % (room.name, room.active_song_id))
            room.status = 1

            self.send_end_score(room, session)

    def send_end_score(self, room, session):
        packet = smpacket.SMPacketServerNSCGON(
            nb_players=0)

        options = ("score", "grade", "difficulty", "miss", "bad", "good", "great", "perfect", "flawless", "held", "max_combo", "options")
        for option in options:
            packet[option] = []

        packet["ids"] = []

        for user in room.users:
            if not user.online:
                continue

            songstat = (session.query(models.SongStat)
                        .filter_by(user_id=user.id, song_id=room.active_song_id)
                        .order_by(models.SongStat.id.desc())
                        .first())

            if not songstat:
                continue

            packet["nb_players"] += 1
            packet["ids"].append(models.User.user_index(user.id, session))

            for option in options:
                packet[option].append(getattr(songstat, option, None))

        self.server.sendroom(room.id, packet)

    def room_still_in_game(self, room, session):
        for conn in self.server.room_connections(room.id):
            if conn.ingame is True:
                return True

        return False

    @periodicmethod(1)
    def scoreboard_update(self, session):
        for room in session.query(models.Room).filter_by(status=2):
            self.send_scoreboard(room, session)

    def send_scoreboard(self, room, session):
        scores = []
        for conn in self.server.room_connections(room.id):
            with conn.mutex:
                for user in self.server.get_users(conn.users, session):
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

        scores.sort(key=lambda x: x['score'], reverse=True)

        packet = smpacket.SMPacketServerNSCGSU(
            nb_players=len(scores),
        )

        packet["section"] = 0
        packet["options"] = [models.User.user_index(score["user"].id, session) for score in scores]
        self.server.sendroom(room.id, packet)

        packet["section"] = 1
        packet["options"] = [score["combo"] for score in scores]
        self.server.sendroom(room.id, packet)

        packet["section"] = 2
        packet["options"] = [score["grade"] for score in scores]
        self.server.sendroom(room.id, packet)

    @periodicmethod(1)
    def send_game_start(self, session):
        for conn in self.server.connections:
            with conn.mutex:
                self.check_song_start(session, conn)

    def check_song_start(self, session, conn):
        if not conn.room or not conn.song:
            return

        if not conn.wait_start:
            return

        if "start_at" not in conn.songstats:
            return

        if datetime.datetime.now() - conn.songstats["start_at"] < datetime.timedelta(seconds=3):
            return

        self.server.log.info("Room %s start a new song %s" % (conn.room, conn.song))

        room = session.query(models.Room).get(conn.room)
        song = session.query(models.Room).get(conn.song)

        StartGameRequestController.launch_song(room, song, self.server)

