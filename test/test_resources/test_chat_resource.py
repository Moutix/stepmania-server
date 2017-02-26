""" Test for chat resource """

import mock

from smserver import exceptions
from smserver import event
from smserver.resources.chat_resource import ChatResource

from test.factories.user_factory import UserFactory
from test.factories.room_factory import RoomFactory
from test.test_resources import base

class ChatResourceTest(base.ResourceTest):
    """ Chat resource class test """

    def setUp(self):
        super().setUp()

        self.resource = ChatResource(self.server, self.token, self.session)

    @mock.patch("smserver.messaging.Messaging.send")
    def test_send_message(self, send_message):
        """ Test sending a message """

        with self.assertRaises(exceptions.Unauthorized):
            self.resource.send("bla")

        send_message.assert_not_called()

        UserFactory(online=True, connection=self.connection)

        self.resource.send("bla")
        send_message.assert_called_once()

        msg = send_message.call_args[0][0]

        self.assertEqual(msg.kind, event.EventKind.chat_message)
        self.assertEqual(msg.token, self.token)
        self.assertIsNone(msg.room_id)

        self.assertEqual(msg.data["message"], "bla")
        self.assertIsNone(msg.data["target"])

    @mock.patch("smserver.messaging.Messaging.send")
    def test_send_room_message(self, send_message):
        """ Test sending a message """

        room = RoomFactory(name="machin")
        UserFactory(online=True, connection=self.connection, room=room)
        self.connection.room = room

        self.resource.send("bla")
        send_message.assert_called_once()

        msg = send_message.call_args[0][0]

        self.assertEqual(msg.kind, event.EventKind.chat_message)
        self.assertEqual(msg.token, self.token)
        self.assertEqual(msg.room_id, room.id)

        self.assertEqual(msg.data["message"], "bla")
        self.assertEqual(msg.data["target"], "~machin")
