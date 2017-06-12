""" Watcher module.

This module is responsible of executing regular task
"""

from threading import Thread
import time
import datetime
import itertools
import socket

from smserver import models
from smserver.smutils.smpacket import smpacket
from smserver.chathelper import with_color
from smserver.controllers.legacy.game_start_request import StartGameRequestController

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
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._continue = True

    def force_run(self):
        with self.server.db.session_scope() as session:
            for func, _ in periodicmethod.functions:
                func(self, session)

                session.commit()

    def run(self):
        self.server.log.debug("Watcher start")
        func_map = {func: 0 for func, _ in periodicmethod.functions}

        while self._continue:
            with self.server.db.session_scope() as session:
                for func, period in periodicmethod.functions:
                    func_map[func] += 1
                    if func_map[func] < period:
                        continue

                    func(self, session)

                    func_map[func] = 0

                    session.commit()

            time.sleep(self.fps)

        self.server.log.info("Successfully close thread: %s", self)

    def stop(self):
        """ End the loop """

        self.server.log.debug("Closing thread: %s", self)
        self._continue = False

    @periodicmethod(5)
    def sdnotify_watchdog(self, _):
        """ Notify systemd that the service is still running """

        if not self.server.is_alive():
            return

        self.server.sd_notify.watchdog()

    @periodicmethod(5)
    def send_udp(self, session):
        packet = smpacket.SMPacketServerNSCFormatted(
            server_name=self.server.config.server["name"],
            server_port=self.server.config.server["port"],
            nb_players=models.User.nb_onlines(session)
        )

        try:
            self._sock.sendto(packet.binary, (self.UDP_IP, self.UDP_PORT))
        except OSError: # Network unreachable
            return

    @periodicmethod(1)
    def send_ping(self, _session):
        self.server.sendall(smpacket.SMPacketServerNSCPing())

    @periodicmethod(2)
    def check_end_game(self, session):
        sendrooms = False
        for room in session.query(models.Room).filter_by(status=2):
            if self.room_still_in_game(room):
                continue

            self.server.log.info("Room %s finish is last song: %s" % (room.name, room.active_song_id))
            room.status = 1
            room.ingame = False

            game = room.last_game
            game.end_at = datetime.datetime.now()
            game.active = False
            self.server.sendplayers(room.id, game.scoreboard_packet)
            self.server.send_message(
                "Game ended %s" % with_color(room.active_song.fullname),
                room
            )
            sendrooms = True
        if sendrooms:
            roomspacket = models.Room.smo_list(session)
            for conn in self.server.connections:
                if conn.room == None:
                    conn.send(roomspacket)
                    self.server.send_user_list_lobby(conn, session)

    def room_still_in_game(self, room):
        for conn in self.server.player_connections(room.id):
            if conn.ingame is True:
                return True

        if room.ingame:
            return False

        # The game is not starded yet, but no NSCGSR have been sent
        if datetime.datetime.now() - room.last_game.created_at > datetime.timedelta(seconds=3):
            return False

        return True

    @periodicmethod(1)
    def scoreboard_update(self, session):
        for room in session.query(models.Room).filter_by(ingame=True):
            self.send_scoreboard(room, session)

    def send_scoreboard(self, room, session):
        scores = []
        for conn in self.server.ingame_connections(room.id):
            connection = models.Connection.by_token(conn.token, session)
            for user in connection.active_users:
                with conn.mutex:
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
        self.server.sendingame(room.id, packet)

        packet["section"] = 1
        packet["options"] = [score["combo"] for score in scores]
        self.server.sendingame(room.id, packet)

        packet["section"] = 2
        packet["options"] = [score["grade"] for score in scores]
        self.server.sendingame(room.id, packet)

    @periodicmethod(1)
    def send_game_start(self, session):
        conn_in_room = itertools.filterfalse(
            lambda x: x.room is None or x.spectate is True,
            self.server.connections)

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
