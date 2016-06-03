#!/usr/bin/env python3
# -*- coding: utf8 -*-

import sys

from smserver.pluginmanager import PluginManager
from smserver.authplugin import AuthPlugin
from smserver.database import DataBase
from smserver.watcher import StepmaniaWatcher
from smserver import conf, logger, models
from smserver.smutils import smthread

def with_session(func):
    """ Wrap the function with a sqlalchemy session.

    Use:
    @with_session
    def func_with_session(self, session):
        pass

    Only work with instance methods of StepmaniaServer class """

    def wrapper(self, *opt):
        with self.db.session_scope() as session:
            func(self, session, *opt)
    return wrapper

class StepmaniaServer(smthread.StepmaniaServer):
    """ Main thread. Start a new thread for each new connections"""

    def __init__(self, config):
        """ Take a config object from smserver.conf and configure the server"""

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
            'smserver.auth.%s' % config.auth["plugin"],
            "AuthPlugin",
            default=AuthPlugin)(self, config.auth["autocreate"])

        self.log.debug("Load Plugins")
        self.plugins = PluginManager("StepmaniaPlugin", config.plugins, "smserver.plugins", "plugin")
        self.plugins.init(self)
        self.controllers = self.init_controllers()
        self.log.debug("Plugins loaded")

        self.log.info("Start server")
        smthread.StepmaniaServer.__init__(self,
                                          config.server["ip"],
                                          config.server["port"])
        self.watcher = StepmaniaWatcher(self)

    def start(self):
        """ Start the main thread and the aynchronous one"""

        self.watcher.start()

        smthread.StepmaniaServer.start(self)

    def init_controllers(self):
        controllers = {}

        for controller in PluginManager("StepmaniaController", None, "smserver.controllers", "controller").values():
            if not controller.command:
                continue

            if controller.command not in controllers:
                controllers[controller.command] = []

            controllers[controller.command].append(controller)
            self.log.debug("Controller loaded for command %s: %s" % (controller.command, controller))

        return controllers

    @with_session
    def on_packet(self, session, serv, packet):
        self.handle_packet(session, serv, packet)

    def handle_packet(self, session, serv, packet):
        for controller in self.controllers.get(packet.command, []):
            app = controller(self, serv, packet, session)

            if app.require_login and not app.active_users:
                self.log.info("Action forbidden %s for user %s" % (packet.command, serv.ip))
                continue

            try:
                app.handle()
            except Exception as err:
                self.log.exception("Message %s %s %s",
                                          type(controller).__name__, controller.__module__, err)
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
        smthread.StepmaniaServer.on_disconnect(self, serv)

        users = self.get_users(serv.users, session)
        if not users:
            self.log.info("Player %s disconnected" % serv.ip)
            return

        for user in users:
            models.User.disconnect(user, session)
            self.log.info("Player %s disconnected" % user.name)

        self.send_user_list(session)

    def send_user_list(self, session):
        self.sendall(models.User.sm_list(session, self.config.server["max_users"]))

    def update_schema(self):
        self.log.info("DROP all the database tables")
        self.db.recreate_tables()

    def get_users(self, user_ids, session):
        if not user_ids:
            return []

        return session.query(models.User).filter(models.User.id.in_(user_ids))

def main():
    config = conf.Conf(*sys.argv[1:])

    StepmaniaServer(config).start()

if __name__ == "__main__":
    main()

