""" Test event module """

import unittest

from smserver import event

class EventTest(unittest.TestCase):
    """ Test event module """

    def test_invalid_message(self):
        """ Test invalid message """

        with self.assertRaises(ValueError):
            event.Event.decode("bla")

    def test_encode_decode(self):
        """ Test encoding and decoding a message """

        msg = event.Event(
            event.EventKind.chat_message,
            data={"a": "b"},
            token="bla",
            room_id=3,
        )

        msg_after_decode = event.Event.decode(msg.encode())

        self.assertEqual(msg, msg_after_decode)
        self.assertEqual(msg.kind, msg_after_decode.kind)
        self.assertEqual(msg.data, msg_after_decode.data)
        self.assertEqual(msg.token, msg_after_decode.token)
        self.assertEqual(msg.room_id, msg_after_decode.room_id)
