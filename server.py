#!/usr/bin/env python3
# -*- coding: utf8 -*-

import sys
import hashlib

from smutils import smserver, smpacket
from pluginmanager import PluginManager
from authplugin import AuthPlugin
from database import DataBase
import conf
import logger
import models

def with_session(func):
    def wrapper(self, *opt):
        with self.db.session_scope() as session:
            func(self, session, *opt)
    return wrapper

class StepmaniaServer(smserver.StepmaniaServer):
    def __init__(self, config):
        self.config = config

        self.log = logger.Logger(config.logger).logger

        self.log.debug("Configuration loaded")

        self.log.debug("Init database")
        self.db = DataBase(
            type=config.database.get("type", 'sqlite'),
            database=config.database.get("database"),
            user=config.database.get("user"),
            password=config.database.get("password"),
            host=config.database.get("host"),
            port=config.database.get("port"),
            driver=config.database.get("driver"),
        )

        if self.config.database["update_schema"]:
            self.update_schema()
        else:
            self.db.create_tables()

        with self.db.session_scope() as session:
            models.User.disconnect_all(session)
            models.Room.init_from_hashes(config.get("rooms", []), session)

        self.auth = PluginManager.import_plugin(
            'auth.%s' % config.auth["plugin"],
            "AuthPlugin",
            default=AuthPlugin)(self, config.auth["autocreate"])

        self.log.debug("Load Plugins")
        self.plugins = PluginManager("StepmaniaPlugin", config.plugins, "plugins", "plugin")
        self.plugins.init(self)
        self.log.debug("Plugins loaded")

        self.log.debug("Start server")
        smserver.StepmaniaServer.__init__(self,
                                          config.server["ip"],
                                          config.server["port"])

    def on_packet(self, serv, packet):
        smserver.StepmaniaServer.on_packet(self, serv, packet)

        for app in self.plugins.values():
            func = getattr(app, "on_%s" % packet.command.name.lower(), None)
            if not func:
                continue

            with self.db.session_scope() as session:
                try:
                    func(session, serv, packet)
                except Exception as err:
                    self.log.exception("Message %s %s %s",
                                       type(app).__name__, app.__module__, err)

    def on_nschello(self, serv, packet):
        serv.stepmania_version = packet["version"]
        serv.stepmania_name = packet["name"]

        serv.send(smpacket.SMPacketServerNSCHello(
            version=128,
            name=self.config.server["name"]))

    @with_session
    def on_nscsu(self, session, serv, packet):
        users = self.get_users(serv.users, session)
        if not users:
            return

        for user in users:
            if user.pos == packet["player_id"]:
                user.online = True
                continue

            if packet["nb_players"] == 1:
                user.online = False
                continue

            user.online = True

        self.log.debug("New list of players: %s" % serv.users)

    @with_session
    def on_nsscsms(self, session, serv, packet):
        users = self.get_users(serv.users, session)
        if not users:
            return

        status_mapping = {
            1: models.UserStatus.music_selection,
            3: models.UserStatus.option,
            5: models.UserStatus.evaluation,
            7: models.UserStatus.room_selection
        }

        if packet["action"] == 7:
            serv.send(models.Room.smo_list(session))

        for user in users:
            user.status = status_mapping.get(packet["action"], models.UserStatus.unknown).value

    @with_session
    def on_login(self, session, serv, packet):
        connected = self.auth.login(packet["username"], packet["password"])

        if not connected:
            self.log.info("Player %s failed to connect" % packet["username"])
            serv.send(smpacket.SMPacketServerNSSMONL(
                packet=smpacket.SMOPacketServerLogin(
                    approval=1,
                    text="Connection failed"
                )
            ))
            return

        user = models.User.connect(packet["username"], packet["player_number"], session)

        user.last_ip = serv.ip
        user.stepmania_name = serv.stepmania_name
        user.stepmania_version = serv.stepmania_version

        for online_user in self.get_users(serv.users, session):
            if online_user.pos == packet["player_number"] and online_user.name != user.name:
                online_user.pos = None
                online_user.online = False
                serv.users.remove(online_user.id)

        if user.id not in serv.users:
            serv.users.append(user.id)

        serv.send(smpacket.SMPacketServerNSSMONL(
            packet=smpacket.SMOPacketServerLogin(
                approval=0,
                text="Successfully login"
            )
        ))
        self.sendall(models.User.sm_list(session, self.config.server["max_users"]))
        serv.send(models.Room.smo_list(session))

    @with_session
    def on_disconnect(self, session, serv):
        users = self.get_users(serv.users, session)
        if not users:
            self.log.info("Player %s disconnected" % serv.ip)
            return

        for user in users:
            models.User.disconnect(user, session)
            self.log.info("Player %s disconnected" % user.name)

    @with_session
    def on_enterroom(self, session, serv, packet):
        users = self.get_users(serv.users, session)
        if not users:
            self.log.info("User unknown return")
            return

        if packet["enter"] == 0:
            serv.send(models.Room.smo_list(session))
            for user in users:
                user.room = None
            return

        room = models.Room.login(packet["room"], packet["password"], session)


        if not room:
            self.log.info("Player %s fail to enter in room %s" % (serv.ip, packet["room"]))
            return


        for user in users:
            user.room = room
            self.log.info("Player %s enter in room %s" % (user.name, room.name))

        serv.send(smpacket.SMPacketServerNSSMONL(
            packet=room.to_packet()
        ))

    @with_session
    def on_createroom(self, session, serv, packet):
        room = models.Room(
            name=packet["title"],
            description=packet["description"],
            type=packet["type"],
            password=hashlib.sha256(packet["password"].encode('utf-8')).hexdigest() if packet["password"] else None,
            status=2,
        )
        session.add(room)

        self.log.info("New room %s created by player %s" % (room.name, serv.ip))

        serv.send(smpacket.SMPacketServerNSSMONL(
            packet=room.to_packet()
        ))

        self.sendall(models.Room.smo_list(session))

    def on_roominfo(self, serv, packet):
        pass

    def update_schema(self):
        self.log.info("DROP all the database tables")
        self.db.recreate_tables()

    def get_users(self, user_ids, session):
        return [self.get_user(user_id, session) for user_id in user_ids]

    def get_user(self, user_id, session):
        if not user_id:
            return None

        return session.query(models.User).get(user_id)

def main():
    config = conf.Conf(*sys.argv[1:])

    StepmaniaServer(config).start()

if __name__ == "__main__":
    main()

