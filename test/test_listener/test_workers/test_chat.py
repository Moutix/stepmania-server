""" Test Chat worker module """

import mock

from smserver import server
from smserver.listener.workers import chat
from smserver.smutils.smpacket import smpacket

from test import utils
from test.factories.room_factory import RoomFactory
from test.factories.connection_factory import ConnectionFactory
from test.factories.user_factory import UserFactory


class ChatWorkerTest(utils.DBTest):
    """ Test listener module """

    def setUp(self):
        super().setUp()

        self.server = server.StepmaniaServer()
        self.worker = chat.ChatWorker(self.server)

    @mock.patch("smserver.smutils.smthread.StepmaniaServer.sendroom")
    @mock.patch("smserver.smutils.smthread.StepmaniaServer.sendconnection")
    def test_handle_room_message(self, sendconnection, sendroom):
        """ Test handling an incomming message """

        room = RoomFactory(name="room_name")
        connection = ConnectionFactory()
        user = UserFactory(connection=connection, online=True, room=room)

        self.worker.handle(
            {
                "target": {"type": "room", "value": room.id},
                "message": "message",
                "source": connection.token
            },
            token=connection.token,
            session=self.session,
        )

        sendconnection.assert_not_called()
        sendroom.assert_called_once()
        self.assertEqual(sendroom.call_args[0][0], room.id)
        packet = sendroom.call_args[0][1]

        self.assertIsInstance(packet, smpacket.SMPacketServerNSCCM)
        self.assertRegex(packet["message"], "room_name")
        self.assertRegex(packet["message"], "message")
        self.assertRegex(packet["message"], user.name)

    @mock.patch("smserver.smutils.smthread.StepmaniaServer.sendroom")
    @mock.patch("smserver.smutils.smthread.StepmaniaServer.sendconnection")
    def test_handle_user_message(self, sendconnection, sendroom):
        """ Test handling an incomming message """

        connection = ConnectionFactory()
        user = UserFactory(connection=connection, online=True)

        connection_target = ConnectionFactory()

        self.worker.handle(
            {
                "target": {"type": "token", "value": connection_target.token},
                "message": "message",
                "source": connection.token
            },
            token=connection.token,
            session=self.session,
        )

        sendroom.assert_not_called()
        sendconnection.assert_called_once()
        self.assertEqual(sendconnection.call_args[0][0], connection_target.token)
        packet = sendconnection.call_args[0][1]

        self.assertIsInstance(packet, smpacket.SMPacketServerNSCCM)
        self.assertRegex(packet["message"], "message")
        self.assertRegex(packet["message"], user.name)


    @mock.patch("smserver.smutils.smthread.StepmaniaServer.sendconnection")
    def test_send_message_token(self, sendconnection):
        """ Test sending a message to a specific connection """

        self.worker.send_message_token("bla", "token")

        sendconnection.assert_called_once()
        self.assertEqual(sendconnection.call_args[0][0], 'token')

        packet = sendconnection.call_args[0][1]

        self.assertEqual(packet["message"], "bla")
        self.assertIsInstance(packet, smpacket.SMPacketServerNSCCM)


    @mock.patch("smserver.smutils.smthread.StepmaniaServer.sendroom")
    def test_send_message_room(self, sendroom):
        """ Test sending a message to a specific room """

        self.worker.send_message_room("bla", None)

        self.assertLog("WARNING")
        sendroom.assert_not_called()

        room = RoomFactory(name="room_name")
        self.worker.send_message_room("bla", room)

        sendroom.assert_called_once()
        self.assertEqual(sendroom.call_args[0][0], room.id)
        packet = sendroom.call_args[0][1]

        self.assertIsInstance(packet, smpacket.SMPacketServerNSCCM)
        self.assertRegex(packet["message"], "room_name")
        self.assertRegex(packet["message"], "bla")
