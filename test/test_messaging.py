""" Test message module """

import unittest
import threading
import time

from smserver import messaging
from smserver import redis_database

class MessageTest(unittest.TestCase):
    """ Test messaging module """

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

        messager.send("Message 1")
        messager.send("Message 2")

        messager.stop()
        time.sleep(0.1)
        self.assertFalse(thread.is_alive())
        self.assertEqual(messages, ["Message 1", "Message 2"])

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

        messager.send("Message 1")
        messager.send("Message 2")

        time.sleep(0.1)
        messager.stop()
        time.sleep(0.1)
        self.assertFalse(thread.is_alive())
        self.assertEqual(messages, ["Message 1", "Message 2"])
