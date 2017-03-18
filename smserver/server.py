""" Server module """

import datetime
from functools import wraps

from smserver import __version__
from smserver import database
from smserver import conf
from smserver import logger
from smserver import models
from smserver import router
from smserver import sdnotify
from smserver import profiling

from smserver.pluginmanager import PluginManager
from smserver.watcher import StepmaniaWatcher
from smserver.chathelper import with_color
from smserver.smutils import smthread
from smserver.smutils.smpacket import smpacket

def with_session(func):
    """ Wrap the function with a sqlalchemy session.

    Use::

        @with_session
        def func_with_session(self, session):
            pass

    Only work with instance methods of StepmaniaServer class """

    @wraps(func)
    def wrapper(self, *arg, **kwargs):
        with self.db.session_scope() as session:
            func(self, session, *arg, **kwargs)
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

    def __init__(self):
        """
            Take a configuration and initialize the server:
            * Load the plugins
            * Load the controllers
            * Load the chat command available
            * Initialize the connection handler

            If no configuration are passed, it will use the default one.
        """

        self.sd_notify = sdnotify.get_notifier()

        self.config = conf.config

        self.log = logger.get_logger()
        self.log.debug("Configuration loaded")

        self.db = database.get_current_db()

        self._init_database()

        self.log.debug("Load plugins...")
        self.sd_notify.status("Load plugins...")

        self.router = router.get_router()
        self.plugins = self._init_plugins()
        self.chat_commands = self._init_chat_commands()
        self.log.debug("Plugins loaded")

        self.log.info("Init server listenner...")
        self.sd_notify.status("Start server listenner...")

        if self.config.server.get("type") not in self.SERVER_TYPE:
            server_type = "async"
        else:
            server_type = self.config.server["type"]

        servers = [
            (self.config.server["ip"], self.config.server["port"], server_type),
        ]

        for server in self.config.additional_servers:
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
        self.send_sd_running_status()

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
        """ Reload configuration files """

        self.sd_notify.reloading()

        self.sd_notify.status("Reloading")
        self.log.info("Reload configuration file")

        self.config.reload()

        self.log.info("Reload plugins")
        self.plugins = self._init_plugins(True)
        self.chat_commands = self._init_chat_commands(True)

        self.log.info("Plugins reloaded")

        self.send_sd_running_status()
        self.sd_notify.ready()

    def send_sd_running_status(self, session=None):
        """ Send running status to systemd """

        if not session:
            with self.db.session_scope() as session:
                nb_onlines = models.User.nb_onlines(session)
        else:
            nb_onlines = models.User.nb_onlines(session)

        max_users = self.config.server.get("max_users", -1)

        self.sd_notify.status(
            "Running. SMServer v%s, started on %s. %s/%s users online" % (
                __version__,
                self.started_at.strftime("%x at %X"),
                nb_onlines,
                max_users if max_users > 0 else "--"
            )
        )

    @with_session
    def add_connection(self, session, conn): #pylint: disable=arguments-differ
        """ Add a new connection """

        if models.Ban.is_ban(session, conn.ip):
            self.log.info("Reject connection from ban ip %s", conn.ip)
            conn.close()
            return

        models.Connection.create(
            session=session,
            ip=conn.ip,
            port=conn.port,
            token=conn.token,
        )
        super().add_connection(conn)
        self.send_sd_running_status()

    @with_session
    @profiling.profile("packet")
    def on_packet(self, session, serv, packet): #pylint: disable=arguments-differ
        self.handle_packet(session, serv, packet)

    def handle_packet(self, session, serv, packet):
        """
            Handle the given packet for a specific connection.

            It will launch every controllers that fetch the packet requirement
            and try to run every plugins.
        """

        self.router.route(
            server=self,
            connection=serv,
            packet=packet,
            session=session
        )

        for app in self.plugins:
            func = getattr(app, "on_%s" % packet.command.name.lower(), None)
            if not func:
                continue

            try:
                func(session, serv, packet)
            except Exception as err: #pylint: disable=broad-except
                self.log.exception("Message %s %s %s",
                                   type(app).__name__, app.__module__, err)
            session.commit()


    @with_session
    def on_disconnect(self, session, conn): #pylint: disable=arguments-differ
        """
            Action to be done when someone is disconected.

            :param session: A database session
            :param serv: The connection to disconnect
            :type session: sqlalchemy.orm.session.Session
            :type serv: smserver.smutils.smconn.StepmaniaConn
        """

        connection = models.Connection.by_token(conn.token, session)

        room = connection.room
        smthread.StepmaniaServer.on_disconnect(self, conn)

        self.send_sd_running_status(session)

        users = connection.active_users
        if not users:
            self.log.info("Player %s disconnected", conn.ip)

        for user in users:
            models.User.disconnect(user, session)
            self.log.info("Player %s disconnected", user.name)

        if room:
            self.send_message(
                "%s disconnected" % models.User.colored_users_repr(users, room.id),
                room=room
            )

            self.send_user_list(room)

        models.Connection.remove(conn.token, session)


    def send_user_list(self, room):
        """
            Send a NSCUUL packet to update the use list for a given room
        """

        self.sendroom(room.id, room.nsccuul)

    def send_message(self, message, room=None, conn=None, func=None):
        """
            Send a chat message (default to all)

            :param str message: The message to send.
            :param room: If specified send to this room
            :param conn: If specified send to this connection
            :param func: If specified use this function to send the message
            :type room: smserver.models.room.Room
            :type conn: smserver.smutils.smconn.StepmaniaConn
        """


        packet = smpacket.SMPacketServerNSCCM(message=message)

        if conn:
            conn.send(packet)
            return

        if not room:
            self.sendall(packet)
            return

        packet["message"] = "#%s %s" % (with_color(room.name), message)
        if not func:
            func = self.sendroom

        func(room.id, packet)

    def disconnect_user(self, user_id):
        """ Disconnect the given user """

        connection = self.find_connection(user_id)
        if not connection:
            return

        connection.close()
        return True

    def _init_database(self):
        with self.db.session_scope() as session:
            models.User.disconnect_all(session)
            models.Room.init_from_hashes(self.config.get("rooms", []), session)
            models.Room.reset_room_status(session)
            models.Ban.reset_ban(session, fixed=True)

            if self.config.get("ban_ips"):
                for ip in self.config.get("ban_ips", []):
                    models.Ban.ban(session, ip, fixed=True)


    def _init_chat_commands(self, force_reload=False):
        chat_commands = {}

        chat_classes = PluginManager(
            plugin_class="ChatPlugin",
            directory="smserver.chat_commands",
            force_reload=force_reload
        )

        chat_classes.extend(
            self._get_plugins("ChatPlugin", force_reload)
        )

        chat_classes.init(self)

        for chat_class in chat_classes:
            if not chat_class.command:
                continue

            chat_commands[chat_class.command] = chat_class
            self.log.debug("Chat command loaded for command %s: %s", chat_class.command, chat_class)

        return chat_commands

    def _init_plugins(self, force_reload=False):
        plugins = self._get_plugins("StepmaniaPlugin", force_reload)

        plugins.init(self)

        return plugins

    def _get_plugins(self, plugin_class, force_reload=False):
        return PluginManager(
            plugin_class=plugin_class,
            paths=self.config.plugins.keys(),
            directory="smserver.plugins",
            plugin_file="plugin",
            force_reload=force_reload
        )
