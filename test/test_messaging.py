""" Test message module """

import unittest
import threading
import time

import mock

from smserver import event
from smserver import messaging
from smserver import redis_database


class MessagingTest(unittest.TestCase):
    """ Test messaging module """

    @mock.patch("smserver.messaging.Messaging.send")
    def test_send_event(self, send):
        """ Test sending a message with the global helper """

        messaging.send_event(event.EventKind.chat_message, "bla")

        send.assert_called_once()
        msg = send.call_args[0][0]

        self.assertEqual(msg.kind, event.EventKind.chat_message)
        self.assertEqual(msg.data, "bla")

    @staticmethod
    @mock.patch("smserver.messaging.Messaging.send")
    def test_send(send):
        """ Test sending a message with the global helper """

        msg = event.Event(event.EventKind.chat_message)

        messaging.send(msg)

        send.assert_called_once_with(msg)


    @mock.patch("smserver.messaging.Messaging.listen")
    def test_listen(self, listen):
        """ Test listen for incomming message  with the global helper """

        listen.return_value = ["bla", "blabla"]

        messages = [msg for msg in messaging.listen()]

        self.assertEqual(messages, ["bla", "blabla"])

    @staticmethod
    @mock.patch("smserver.messaging.Messaging.stop")
    def test_stop(stop):
        """ Test stop listenning with the global helper """

        messaging.stop()
        stop.assert_called_once_with()

    def test_message_without_handler(self):
        """ Test to send message without handler configured """

        messager = messaging.Messaging()

        with self.assertRaises(ValueError):
            messager.send("bla")

        with self.assertRaises(ValueError):
            for _ in messager.listen():
                pass

        with self.assertRaises(ValueError):
            messager.stop()

    def test_message_with_python_handler(self):
        """ Test messaging with python handler """

        messager = messaging.Messaging()
        messager.set_handler(messaging.PythonHandler())

        messages = []

        def receive_msg():
            """ Worker thread which add message to messages """

            for msg in messager.listen():
                messages.append(msg)

        thread = threading.Thread(target=receive_msg)
        thread.start()
        time.sleep(0.1)

        msg1 = event.Event(event.EventKind.chat_message, data={"bla": "bla"})
        msg2 = event.Event(event.EventKind.chat_message)
        msg_invalid = "Bla"

        messager.send(msg1)
        messager.send(msg2)
        with self.assertRaises(ValueError):
            messager.send(msg_invalid)

        messager.stop()
        time.sleep(0.1)
        self.assertFalse(thread.is_alive())
        self.assertEqual(messages, [msg1, msg2])
        self.assertEqual(messages[0].data, msg1.data)
        self.assertEqual(messages[0].kind, msg1.kind)
        self.assertEqual(messages[1].data, msg2.data)
        self.assertEqual(messages[1].kind, msg2.kind)

    def test_message_with_redis_handler(self):
        """ Test messaging with redis """

        if not redis_database.is_available():
            self.skipTest("Redis is not configured")

        messager = messaging.Messaging()
        messager.set_handler(messaging.RedisHandler())

        messages = []

        def receive_msg():
            """ Worker thread which add message to messages """

            for msg in messager.listen():
                messages.append(msg)

        thread = threading.Thread(target=receive_msg)
        thread.start()
        time.sleep(0.1)

        msg1 = event.Event(event.EventKind.chat_message, data={"bla": "bla"})
        msg2 = event.Event(event.EventKind.chat_message)

        msg_invalid = "Bla"

        messager.send(msg1)
        messager.send(msg2)
        with self.assertRaises(ValueError):
            messager.send(msg_invalid)

        time.sleep(0.1)

        messager.stop()
        time.sleep(0.1)
        self.assertFalse(thread.is_alive())

        self.assertEqual(messages, [msg1, msg2])
        self.assertEqual(messages[0].data, msg1.data)
        self.assertEqual(messages[0].kind, msg1.kind)
        self.assertEqual(messages[1].data, msg2.data)
        self.assertEqual(messages[1].kind, msg2.kind)
