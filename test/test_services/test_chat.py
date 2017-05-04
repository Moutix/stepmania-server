""" Service chat test module """

import unittest

import mock

from smserver import event
from smserver import services

class ChatServiceTest(unittest.TestCase):
    """ Test services chat """

    @mock.patch("smserver.messaging.Messaging.send")
    def test_send_message_token(self, send_message):
        """ Test sending message to a token """

        services.chat.send_message_token(
            token="token",
            message="bla",
            source="moi"
        )

        send_message.assert_called_once()

        msg = send_message.call_args[0][0]

        self.assertEqual(msg.kind, event.EventKind.chat_message)
        self.assertEqual(msg.token, "moi")
        self.assertIsNone(msg.room_id)

        self.assertEqual(msg.data["message"], "bla")
        self.assertEqual(msg.data["target"]["value"], "token")
        self.assertEqual(msg.data["target"]["type"], "token")

    @mock.patch("smserver.messaging.Messaging.send")
    def test_send_message_room(self, send_message):
        """ Test sending message to a token """

        services.chat.send_message_room(
            room_id=42,
            message="bla",
            source="moi"
        )

        send_message.assert_called_once()

        msg = send_message.call_args[0][0]

        self.assertEqual(msg.kind, event.EventKind.chat_message)
        self.assertEqual(msg.token, "moi")
        self.assertEqual(msg.room_id, 42)

        self.assertEqual(msg.data["message"], "bla")
        self.assertEqual(msg.data["target"]["value"], 42)
        self.assertEqual(msg.data["target"]["type"], "room")
