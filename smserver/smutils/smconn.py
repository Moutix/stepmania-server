#!/usr/bin/env python3
# -*- coding: utf8 -*-

import datetime
import logging
from threading import Thread, Lock

class StepmaniaConn(Thread):
    logger = logging.getLogger('stepmania')

    def __init__(self, serv, conn, ip, port):
        Thread.__init__(self)
        self.mutex = Lock()
        self.ip = ip
        self.port = port
        self.users = []
        self.room = None
        self.logged_users = []
        self.songs = {}
        self.song = None
        self.songstats = {0: {"data": []}, 1: {"data": []}}
        self.wait_start = False
        self.ingame = False

        self.last_ping = datetime.datetime.now()
        self.stepmania_version = None
        self.stepmania_name = None
        self._serv = serv
        self._conn = conn

        self.logger.info("New connection: %s on port %s" % (ip, port))

    def run(self):
        for data in self.received_data():
            if data is None:
                break

            self._on_data(data)

        self.close()

    def received_data(self):
        pass

    def _on_data(self, data):
        pass

    def send(self, packet):
        pass

    def close(self):
        self._serv.on_disconnect(self)
        self._conn.close()

