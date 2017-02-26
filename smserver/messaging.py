""" Messaging module

Us to send messages between process and thread
"""

import abc
import queue

from smserver import redis_database
from smserver import event


class Messaging(object):
    """ Message class """

    def __init__(self, handler=None):
        self._handler = handler

    def send(self, message):
        """ Send a message to all the listener """
        if not self._handler:
            raise ValueError("No handler configured")

        self._handler.send(message)

    def listen(self):
        """ Listen for incomming messages """

        if not self._handler:
            raise ValueError("No handler configured")

        yield from self._handler.listen()

    def set_handler(self, handler):
        """ Set the handler to use """

        self._handler = handler

    def stop(self):
        """ Stop the message listener """

        if not self._handler:
            raise ValueError("No handler configured")

        self._handler.stop()


class MessageHandler(metaclass=abc.ABCMeta):
    """ Abstract class for creating new handler """

    @abc.abstractmethod
    def send(self, message):
        """ How the handler handle the message delivery

            :param smserver.event.Event message: Message to send
        """

        if not isinstance(message, event.Event):
            raise ValueError("Messaging only support Event object")


    @abc.abstractmethod
    def listen(self):
        """ How the handler listen for incomming message """

    @abc.abstractmethod
    def stop(self):
        """ Stop the listener """

class PythonHandler(MessageHandler):
    """ Python handler use when using the server in only one process """

    def __init__(self):
        self._queue = queue.Queue()

    def send(self, message):
        """ Send the message to the queue """

        super().send(message)

        self._queue.put(message)

    def listen(self):
        """ Process message from the queue """

        while True:
            message = self._queue.get()
            if message is None:
                break

            yield message
            self._queue.task_done()

    def stop(self):
        """ Stop the listener by adding a None element to the queue """

        self._queue.put(None)


class RedisHandler(MessageHandler):
    """ Redis Handler. Use pub/sub mechanism """

    def __init__(self, channel="socka"):
        self.connection = redis_database.new_connection()
        self.pubsub = self.connection.pubsub(
            ignore_subscribe_messages=True
        )

        self.channel = channel

        self._continue = False

    def send(self, message):
        """ Send a message through a redis chanel """

        super().send(message)

        self.connection.publish(self.channel, message.encode())

    def listen(self):
        """ Listen for message comming through redis """

        self._continue = True
        self.pubsub.subscribe(self.channel)

        while self._continue:
            message = self.pubsub.get_message(timeout=0.01)
            if not message or message["type"] != "message":
                continue

            yield event.Event.decode(message["data"])

        self.pubsub.unsubscribe(self.channel)
        self.pubsub.close()

    def stop(self):
        """ Stop the listener by adding a None element to the queue """

        self._continue = False


_MESSAGING = Messaging()

def set_handler(handler):
    """ Add an handler to the global message class """

    _MESSAGING.set_handler(handler)

def send(message):
    """ Send a message with the global message class """

    _MESSAGING.send(message)

def send_event(kind, data=None, token=None, room_id=None):
    """ Send an event with the global message class """

    _MESSAGING.send(event.Event(
        kind=kind,
        data=data,
        token=token,
        room_id=room_id
    ))

def listen():
    """ Listen for message with the global message class """

    yield from _MESSAGING.listen()


def stop():
    """ Stop to listen """

    _MESSAGING.stop()
