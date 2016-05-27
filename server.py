#!/usr/bin/env python3
# -*- coding: utf8 -*-

import sys

from smutils import smserver
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
        self.controllers = self.init_controllers()
        self.log.debug("Plugins loaded")

        self.log.debug("Start server")
        smserver.StepmaniaServer.__init__(self,
                                          config.server["ip"],
                                          config.server["port"])


    def init_controllers(self):
        controllers = {}

        for controller in PluginManager("StepmaniaController", [], "controllers", "controller").values():
            if not controller.command:
                continue

            if controller.command not in controllers:
                controllers[controller.command] = []

            controllers[controller.command].append(controller)
            self.log.debug("Controller loaded for command %s: %s" % (controller.command, controller))

        self._controllers = controllers

        return controllers

    @with_session
    def on_packet(self, session, serv, packet):
        self.handle_packet(session, serv, packet)

    def handle_packet(self, session, serv, packet):
        for controller in self.controllers.get(packet.command, []):
            controller(self, serv, packet, session).handle()

            session.commit()

        for app in self.plugins.values():
            func = getattr(app, "on_%s" % packet.command.name.lower(), None)
            if not func:
                continue

            try:
                func(session, serv, packet)
            except Exception as err:
                self.log.exception("Message %s %s %s",
                                          type(app).__name__, app.__module__, err)
            session.commit()



    @with_session
    def on_disconnect(self, session, serv):
        users = self.get_users(serv.users, session)
        if not users:
            self.log.info("Player %s disconnected" % serv.ip)
            return

        for user in users:
            models.User.disconnect(user, session)
            self.log.info("Player %s disconnected" % user.name)

    def update_schema(self):
        self.log.info("DROP all the database tables")
        self.db.recreate_tables()

    def get_users(self, user_ids, session):
        return [self.get_user(user_id, session) for user_id in user_ids]

    def get_user(self, user_id, session):
        if not user_id:
            return None

        return session.query(models.User).get(user_id)

    def get_room(self, room_id, session):
        if not room_id:
            return None

        return session.query(models.Room).get(room_id)

def main():
    config = conf.Conf(*sys.argv[1:])

    StepmaniaServer(config).start()

if __name__ == "__main__":
    main()

