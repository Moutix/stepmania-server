#!/usr/bin/env python3
# -*- coding: utf8 -*-

import sys
import datetime

from smserver.pluginmanager import PluginManager
from smserver.authplugin import AuthPlugin
from smserver.database import DataBase
from smserver.watcher import StepmaniaWatcher
from smserver import conf, logger, models, sdnotify
from smserver.smutils import smthread

def with_session(func):
    """ Wrap the function with a sqlalchemy session.

    Use::

        @with_session
        def func_with_session(self, session):
            pass

    Only work with instance methods of StepmaniaServer class """

    def wrapper(self, *opt):
        with self.db.session_scope() as session:
            func(self, session, *opt)
    return wrapper

class StepmaniaServer(smthread.StepmaniaServer):
    """
        It's the main class of the server. It will start a new thread for each
        configured server.

        To start the server you will generally use::

            from smserver import conf, server

            config = conf.Conf(*sys.argv[1:])

            server.StepmaniaServer(config).start()
    """

    def __init__(self, config=None):
        """
            Take a configuration and initialize the server:

            * Load the database and create the tables if needed
            * Load the plugins
            * Load the controllers
            * Load the chat command available
            * Initialize the connection handler

            If no configuration are passed, it will use the default one.
        """

        self.sd_notify = sdnotify.SDNotify()

        if not config:
            config = conf.Conf()

        self.config = config

        self.log = logger.Logger(config.logger).logger
        self.log.debug(self.sd_notify)

        self.log.debug("Configuration loaded")
        self.log.debug(self.sd_notify.available)

        self.log.debug("Init database")
        self.sd_notify.status("Init database")

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
            self._update_schema()
        else:
            self.db.create_tables()

        with self.db.session_scope() as session:
            models.User.disconnect_all(session)
            models.Room.init_from_hashes(config.get("rooms", []), session)
            models.Room.reset_room_status(session)
            models.Ban.reset_ban(session, fixed=True)

            if self.config.get("ban_ips"):
                for ip in self.config.get("ban_ips", []):
                    models.Ban.ban(session, ip, fixed=True)

        self.log.debug("Load plugins...")
        self.sd_notify.status("Load plugins...")

        self.auth = PluginManager.get_plugin(
            'smserver.auth.%s' % config.auth["plugin"],
            "AuthPlugin",
            default=AuthPlugin)(self, config.auth["autocreate"])


        self.plugins = self._init_plugins()
        self.controllers = self._init_controllers()
        self.chat_commands = self._init_chat_commands()
        self.log.debug("Plugins loaded")

        self.log.info("Init server listenner...")
        self.sd_notify.status("Start server listenner...")

        if config.server.get("type") not in self.SERVER_TYPE:
            server_type = "async"
        else:
            server_type = config.server["type"]

        servers = [
            (config.server["ip"], config.server["port"], server_type),
        ]

        for server in config.additional_servers:
            servers.append((server["ip"], server["port"], server.get("type")))

        smthread.StepmaniaServer.__init__(self, servers)
        for ip, port, server_type in servers:
            self.log.info("Server %s listening on %s:%s", server_type, ip, port)

        self.watcher = StepmaniaWatcher(self)

        self.started_at = datetime.datetime.now()

    def start(self):
        """ Start all the threads """

        self.watcher.start()
        self.sd_notify.ready()
        self.sd_notify.status("Running")

        smthread.StepmaniaServer.start(self)

    def stop(self):
        """ Close all the threads """

        self.sd_notify.stopping()
        self.sd_notify.status("Stopping...")

        self.log.info("Disconnect all client...")
        for connection in self.connections:
            connection.close()

        self.log.info("Closing all the threads...")

        self.watcher.stop()
        for server in self._servers:
            server.stop()

        self.watcher.join()
        for server in self._servers:
            server.join()

    def reload(self):
        """ Relaod configuration files """

        self.sd_notify.reloading()

        self.sd_notify.status("Reloading")
        self.log.info("Reload configuration file")

        self.config.reload()

        self.log.info("Reload plugins")
        self.plugins = self._init_plugins()
        self.controllers = self._init_controllers()
        self.chat_commands = self._init_chat_commands()

        self.log.info("Plugins reloaded")

        self.sd_notify.status("Running")
        self.sd_notify.ready()

    @with_session
    def add_connection(self, session, conn):
        if models.Ban.is_ban(session, conn.ip):
            self.log.info("Reject connection from ban ip %s", conn.ip)
            conn.close()
            return

        smthread.StepmaniaServer.add_connection(self, conn)

    @with_session
    def on_packet(self, session, serv, packet):
        self.handle_packet(session, serv, packet)

    def handle_packet(self, session, serv, packet):
        """
            Handle the given packet for a specific connection.

            It will launch every controllers that fetch the packet requirement
            and try to run every plugins.
        """

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

        for app in self.plugins:
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
        """
            Action to be done when someone is disconected.

            :param session: A database session
            :param serv: The connection to disconnect
            :type session: sqlalchemy.orm.session.Session
            :type serv: smserver.smutils.smconn.StepmaniaConn
        """

        room_id = serv.room
        smthread.StepmaniaServer.on_disconnect(self, serv)

        users = models.User.get_from_ids(serv.users, session)
        if not users:
            self.log.info("Player %s disconnected" % serv.ip)
            return

        for user in users:
            models.User.disconnect(user, session)
            self.log.info("Player %s disconnected" % user.name)

        if room_id:
            room = session.query(models.Room).get(room_id)
            self.send_user_list(room)

    def send_user_list(self, room):
        """
            Send a NSCUUL packet to update the use list for a given room
        """

        self.sendroom(room.id, room.nsccuul)

    def _init_controllers(self):
        controllers = {}

        controller_classes = PluginManager("StepmaniaController", None, "smserver.controllers")

        controller_classes.extend(PluginManager(
            "StepmaniaController",
            self.config.plugins,
            "smserver.plugins",
            "plugin"
        ))

        for controller in controller_classes:
            if not controller.command:
                continue

            if controller.command not in controllers:
                controllers[controller.command] = []

            controllers[controller.command].append(controller)
            self.log.debug("Controller loaded for command %s: %s" % (controller.command, controller))

        return controllers

    def _init_chat_commands(self):
        chat_commands = {}

        chat_classes = PluginManager("ChatPlugin", None, "smserver.chat_commands")

        chat_classes.extend(PluginManager(
            "ChatPlugin",
            self.config.plugins,
            "smserver.plugins",
            "plugin"
        ))
        chat_classes.init()

        for chat_class in chat_classes:
            if not chat_class.command:
                continue

            chat_commands[chat_class.command] = chat_class
            self.log.debug("Chat command loaded for command %s: %s" % (chat_class.command, chat_class))

        return chat_commands

    def _init_plugins(self):
        plugins = PluginManager("StepmaniaPlugin", self.config.plugins.keys(), "smserver.plugins", "plugin")
        plugins.init(self)

        return plugins

    def _update_schema(self):
        self.log.info("DROP all the database tables")
        self.db.recreate_tables()


def main():
    config = conf.Conf(*sys.argv[1:])

    StepmaniaServer(config).start()

if __name__ == "__main__":
    main()

