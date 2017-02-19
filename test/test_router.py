""" Test router module """

import mock

from smserver.stepmania_controller import StepmaniaController
from smserver.smutils.smpacket import smcommand
from smserver.smutils.smpacket import smpacket
from smserver.smutils import smconn
from smserver import router
from smserver import server

from test import utils
from test.factories.connection_factory import ConnectionFactory
from test.factories.user_factory import UserFactory


class Controller1(StepmaniaController):
    """ Controller class for testing purpose"""

    require_login = False

class Controller2(StepmaniaController):
    """ Controller class for testing purpose"""

    require_login = True


class RouterTest(utils.DBTest):
    """ Test Stepmania Server class """

    def test_add_route(self):
        """ Test adding a route to the router """

        test_router = router.Router()

        command = smcommand.SMClientCommand.NSCAttack

        test_router.add_route(command, Controller1)
        self.assertEqual(test_router.routes[command], [Controller1])

        test_router.add_route(command, Controller2)
        self.assertEqual(test_router.routes[command], [Controller1, Controller2])

    @mock.patch("test.test_router.Controller2.handle")
    @mock.patch("test.test_router.Controller1.handle")
    def test_route(self, handle_controller1, handle_controller2):
        """ Test routing packet """

        test_router = router.Router()

        serv = server.StepmaniaServer()
        conn = smconn.StepmaniaConn(server, "8.8.8.8", 42)
        connection = ConnectionFactory(token=conn.token)

        command = smcommand.SMClientCommand.NSCAttack
        packet = smpacket.SMPacket.new(command)

        # No route
        test_router.route(serv, conn, packet)
        handle_controller1.assert_not_called()
        handle_controller2.assert_not_called()

        # Route only controller 1
        test_router.add_route(command, Controller1)
        test_router.route(serv, conn, packet, session=self.session)
        handle_controller1.assert_called_with()
        handle_controller1.reset_mock()
        handle_controller2.assert_not_called()

        # Route with require login
        test_router.add_route(command, Controller2)
        test_router.route(serv, conn, packet, session=self.session)
        handle_controller1.assert_called_with()
        handle_controller1.reset_mock()
        handle_controller2.assert_not_called()

        # Test with login user
        UserFactory(connection_token=connection.token, online=True)

        test_router.route(serv, conn, packet, session=self.session)
        handle_controller1.assert_called_with()
        handle_controller2.assert_called_with()
        handle_controller1.reset_mock()
        handle_controller2.reset_mock()

        # With exceptions, no crash
        handle_controller1.side_effect = Exception()
        test_router.route(serv, conn, packet, session=self.session)
        handle_controller1.assert_called_with()
        handle_controller2.assert_called_with()
        handle_controller1.reset_mock()
        handle_controller2.reset_mock()
