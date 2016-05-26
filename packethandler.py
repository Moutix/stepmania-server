#!/usr/bin/env python3
# -*- coding: utf8 -*-

import hashlib

from smutils import smserver, smpacket
import models

class PacketHandler(smserver.PacketHandler):
    def __init__(self, server, conn, packet, session):
        smserver.PacketHandler.__init__(self, server, conn, packet)
        self.session = session
        self.log = self.server.log
        self.room = self.server.get_room(conn.room, session)
        self.users = self.server.get_users(conn.users, session)
        self.active_users = [user for user in self.users if user.online]

    def handle(self):
        smserver.PacketHandler.handle(self)

        self.session.commit()

        for app in self.server.plugins.values():
            func = getattr(app, "on_%s" % self.packet.command.name.lower(), None)
            if not func:
                continue

            try:
                func(self.session, self.conn, self.packet)
            except Exception as err:
                self.server.log.exception("Message %s %s %s",
                                          type(app).__name__, app.__module__, err)
            self.session.commit()

    def on_nssmonl(self):
        PacketHandler(self.server, self.conn, self.packet["packet"], self.session).handle()

    def on_nschello(self):
        self.conn.stepmania_version = self.packet["version"]
        self.conn.stepmania_name = self.packet["name"]

        self.conn.send(smpacket.SMPacketServerNSCHello(
            version=128,
            name=self.server.config.server["name"]))

    def on_nscrsg(self):
        if not self.room:
            return

        song = models.Song.find_or_create(
            self.packet["song_title"],
            self.packet["song_subtitle"],
            self.packet["song_artist"],
            self.session)

        if self.packet["usage"] == 2:
            #TODO: Handle permission, for now just ask to start the song
            self.sendroom(self.room.id, smpacket.SMPacketServerNSCRSG(
                usage=3,
                song_title=song.title,
                song_subtitle=song.subtitle,
                song_artist=song.artist
                ))

    def on_nscsu(self):
        if not self.users:
            return

        for user in self.users:
            if user.pos == self.packet["player_id"]:
                user.online = True
                continue

            if self.packet["nb_players"] == 1:
                user.online = False
                continue

            user.online = True

        self.log.debug("New list of players: %s" % self.conn.users)

    def on_nsscsms(self):
        if not self.active_users:
            return

        status_mapping = {
            1: models.UserStatus.music_selection,
            3: models.UserStatus.option,
            5: models.UserStatus.evaluation,
            7: models.UserStatus.room_selection
        }

        if self.packet["action"] == 7:
            self.send(models.Room.smo_list(self.session))

        for user in self.active_users:
            user.status = status_mapping.get(self.packet["action"], models.UserStatus.unknown).value

    def on_login(self):
        connected = self.server.auth.login(self.packet["username"], self.packet["password"])

        if not connected:
            self.log.info("Player %s failed to connect" % self.packet["username"])
            self.send(smpacket.SMPacketServerNSSMONL(
                packet=smpacket.SMOPacketServerLogin(
                    approval=1,
                    text="Connection failed for user %s" % self.packet["username"]
                )
            ))
            return

        user = models.User.connect(self.packet["username"], self.packet["player_number"], self.session)
        self.log.info("Player %s successfully connect" % self.packet["username"])

        user.last_ip = self.conn.ip
        user.stepmania_name = self.conn.stepmania_name
        user.stepmania_version = self.conn.stepmania_version

        for online_user in self.users:
            if online_user.pos == self.packet["player_number"] and online_user.name != user.name:
                online_user.pos = None
                online_user.online = False

        if user.id not in self.conn.users:
            self.conn.users.append(user.id)

        self.send(smpacket.SMPacketServerNSSMONL(
            packet=smpacket.SMOPacketServerLogin(
                approval=0,
                text="Player %s successfully login" % self.packet["username"]
            )
        ))
        self.sendall(models.User.sm_list(self.session, self.server.config.server["max_users"]))
        self.send(models.Room.smo_list(self.session))

    def on_enterroom(self):
        if not self.active_users:
            self.log.info("User unknown return")
            return

        if self.packet["enter"] == 0:
            self.send(models.Room.smo_list(self.session))
            self.conn.room = None
            for user in self.active_users:
                user.room = None

            return

        room = models.Room.login(self.packet["room"], self.packet["password"], self.session)

        if not room:
            self.log.info("Player %s fail to enter in room %s" % (self.conn.ip, self.packet["room"]))
            return


        self.conn.room = room.id
        for user in self.active_users:
            user.room = room
            self.log.info("Player %s enter in room %s" % (user.name, room.name))

        self.send(smpacket.SMPacketServerNSSMONL(
            packet=room.to_packet()
        ))

    def on_createroom(self):
        room = models.Room(
            name=self.packet["title"],
            description=self.packet["description"],
            type=self.packet["type"],
            password=hashlib.sha256(self.packet["password"].encode('utf-8')).hexdigest() if self.packet["password"] else None,
            status=2,
        )
        self.session.add(room)
        self.session.commit()

        self.log.info("New room %s created by player %s" % (room.name, self.conn.ip))

        self.conn.room = room.id
        for user in self.active_users:
            user.room = room
            self.log.info("Player %s enter in room %s" % (user.name, room.name))

        self.send(smpacket.SMPacketServerNSSMONL(
            packet=room.to_packet()
        ))

        self.sendall(models.Room.smo_list(self.session))

    def on_roominfo(self):
        pass

