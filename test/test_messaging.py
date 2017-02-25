""" Test message module """

import unittest
import threading
import time

from smserver import messaging

class MessageTest(unittest.TestCase):
    """ Test messaging module """

    def test_python_handler(self):
        """ test adding an element to the queue """

        messager = messaging.PythonHandler()

        messager.send("Message")

        messages = []

        def receive_msg():
            """ Worker thread which add message to messages """

            for msg in messager.listen():
                messages.append(msg)

        thread = threading.Thread(target=receive_msg)
        thread.start()

        messager.stop()
        time.sleep(0.1)
        self.assertFalse(thread.is_alive())
        self.assertEqual(messages, ["Message"])

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

    def test_message_with_handler(self):
        """ Test messager send """

        messager = messaging.Messaging()
        messager.set_handler(messaging.PythonHandler())

        messager.send("Message 1")
        messager.send("Message 2")

        messages = []

        def receive_msg():
            """ Worker thread which add message to messages """

            for msg in messager.listen():
                messages.append(msg)

        thread = threading.Thread(target=receive_msg)
        thread.start()

        messager.stop()
        time.sleep(0.1)
        self.assertFalse(thread.is_alive())
        self.assertEqual(messages, ["Message 1", "Message 2"])
