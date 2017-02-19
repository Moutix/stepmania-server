""" Router module """

import collections

from smserver import logger
from smserver.controllers import routes

__all__ = ['Router', 'add_route', 'get_router']


class Router(object):
    """ Router class """

    log = logger.get_logger()

    def __init__(self):
        # We don't use set, because we need order
        self.routes = collections.defaultdict(list)

    def add_route(self, command, controller):
        """ Add a route

            :param command: Route this type of packet
            :type command: smserver.smutils.smpacket.smcommand.SMCommand

            :param controller: The controller to use
            :type controller: smserver.stepmania_controller.StepmaniaController
        """

        self.routes[command].append(controller)

    def load_routes_dict(self, route_dict):
        """ Load a routes dict """

        for command, controller in route_dict.items():
            self.add_route(command, controller)

    def route(self, server, connection, packet, *, session=None):
        """ Route a packet to the correct controller

            :param server: The server wich received the packet
            :type server: smserver.server.StepmaniaServer
            :param connection: The connection that have received the packet
            :type connection: smserver.smutils.smconn.StepmaniaConn
            :param packet: The packet we want to route
            :type packet: smserver.smutils.smpacket.smpacket.SMPacket
        """

        if packet.command not in self.routes:
            self.log.error("Cannot route packet %s from %s", packet, connection)
            return

        with server.db.session_scope(session) as session:
            for i, controller in enumerate(self.routes[packet.command]):
                if i > 0:
                    session.commit()

                app = controller(server, connection, packet, session)

                if app.require_login and not app.active_users:
                    self.log.info("Action forbidden %s for user %s", packet.command, connection.token)
                    continue

                try:
                    app.handle()
                except Exception as err: #pylint: disable=broad-except
                    self.log.exception("Message %s %s %s",
                                       type(controller).__name__, controller.__module__, err)

_ROUTER = Router()
_ROUTER.load_routes_dict(routes.ROUTES)

def add_route(command, controller):
    """ Add a route to th global router """

    _ROUTER.add_route(command, controller)

def get_router():
    """ Get the global router """

    return _ROUTER
