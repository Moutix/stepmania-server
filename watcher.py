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

            time.sleep(self.fps)

    @periodicmethod
    def send_ping(self, session):
        self.server.sendall(smpacket.SMPacketClientNSCPing())

    @periodicmethod
    def send_game_start(self, session):
        for conn in self.server.connections:
            with conn.mutex:
                self.check_song_start(session, conn)

    def check_song_start(self, session, conn):
        if not conn.wait_start:
            return

        if "start_at" not in conn.songs:
            return

        if datetime.datetime.now() - conn.songs["start_at"] < datetime.timedelta(seconds=3):
            return

        room = session.query(models.Room).get(conn.room)
        song = session.query(models.Room).get(conn.song)

        StartGameRequestController.launch_song(room, song, self.server)

