""" Request start game controller """

from smserver.smutils.smpacket import smpacket
from smserver.smutils.smpacket import smcommand
from smserver.stepmania_controller import StepmaniaController
from smserver.chathelper import with_color
from smserver import models, ability

class RequestStartGameController(StepmaniaController):
    command = smcommand.SMClientCommand.NSCRSG
    require_login = True

    def handle(self):
        if not self.room:
            return

        song = models.Song.find_or_create(
            self.packet["song_title"],
            self.packet["song_subtitle"],
            self.packet["song_artist"],
            self.session)

        if self.packet["usage"] == 2:
            self.start_game_request(song)
            return

        have_song = self.check_song_presence(song)

        if not have_song:
            self.send_message("%s does %s have the song (%s)!" % (
                self.colored_user_repr(self.room.id),
                with_color("not", "ff0000"),
                with_color(song.fullname)
                ))

    def start_game_request(self, song):
        with self.conn.mutex:
            self.conn.songs[song.id] = True

        if self.conn.song == song.id:
            self.request_launch_song(song)
            return

        self.send_message("%s select %s which have been played %s times.%s" % (
            self.colored_user_repr(self.room.id),
            with_color(song.fullname),
            song.time_played,
            " Best scores:" if song.time_played > 0 else ""
            ))

        if song.time_played > 0:
            for song_stat in song.best_scores:
                self.send_message(song_stat.pretty_result(room_id=self.room.id, color=True))

        with self.conn.mutex:
            self.conn.song = song.id
            self.conn.songs[song.id] = True

        self.sendplayers(self.room.id, smpacket.SMPacketServerNSCRSG(
            usage=1,
            song_title=song.title,
            song_subtitle=song.subtitle,
            song_artist=song.artist
            ))

    def check_song_presence(self, song):
        with self.conn.mutex:
            self.conn.songs[song.id] = {0: True, 1: False}[self.packet["usage"]]

            return self.conn.songs[song.id]

    def request_launch_song(self, song):
        if not self.room.free and self.cannot(ability.Permissions.start_game, self.room.id):
            self.send_message("You don't have the permission to start a game", to="me")
            return

        if self.room.status == 2 and self.room.active_song_id:
            self.send_message(
                "Room %s is already playing %s." % (
                    with_color(self.room.name),
                    with_color(self.room.active_song.fullname)
                    ),
                to="me"
            )
            return

        game = models.Game(room_id=self.room.id, song_id=song.id)

        self.session.add(game)
        self.session.commit()

        self.send_message("%s started the song %s" % (self.colored_user_repr(self.room.id), with_color(song.fullname)) )
 
        self.room.status = 2
        self.room.active_song = song
        self.sendplayers(self.room.id, smpacket.SMPacketServerNSCRSG(
            usage=2,
            song_title=song.title,
            song_subtitle=song.subtitle,
            song_artist=song.artist
            ))

        roomspacket = models.Room.smo_list(self.session, self.active_users)
        for conn in self.server.connections:
            if conn.room == None:
                conn.send(roomspacket)
                self.server.send_user_list_lobby(conn, self.session)

