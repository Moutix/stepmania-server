#!/usr/bin/env python3
# -*- coding: utf8 -*-

from threading import Thread, Lock
import time
import datetime
import models
from smutils import smpacket
from controllers.game_start_request.controller import StartGameRequestController

class PeriodicMethods(object):
    def __init__(self):
        self.functions = []

    def __call__(self, func):
        self.functions.append(func)
        def wrapper(self, *opts):
            func(self, *opts)

        return wrapper

periodicmethod = PeriodicMethods()

class StepmaniaWatcher(Thread):
    def __init__(self, server):
        Thread.__init__(self)

        self.server = server
        self.fps = self.server.config.server.get("fps", 2)
        self.mutex = Lock()

    def run(self):
        self.server.log.debug("Watcher start")
        while True:
            with self.server.db.session_scope() as session:
                for func in periodicmethod.functions:
                    func(self, session)

                    session.commit()

            time.sleep(self.fps)

    @periodicmethod
    def send_ping(self, session):
        self.server.sendall(smpacket.SMPacketServerNSCPing())

    @periodicmethod
    def check_end_game(self, session):
        for room in session.query(models.Room).filter_by(status=2):
            if self.room_still_in_game(room, session):
                continue

            self.server.log.debug("Room %s finish is last song" % room.name)
            room.status = 1

    def room_still_in_game(self, room, session):
        for conn in self.server.room_connections(room.id):
            if conn.ingame is True:
                return True

        return False

    @periodicmethod
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

        room = session.query(models.Room).get(conn.room)
        song = session.query(models.Room).get(conn.song)

        StartGameRequestController.launch_song(room, song, self.server)

