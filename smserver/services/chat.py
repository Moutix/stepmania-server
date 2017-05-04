""" Chat service """

from smserver import event
from smserver import messaging

def send_message_token(token, message, source=None):
    """
        Send a chat message to the given target

        :param str token: target of the message (token of the connection)
        :param str message: Message to send
        :param str source: token which have send the event
    """

    msg = event.Event(
        kind=event.EventKind.chat_message,
        data={
            "source": source,
            "message": message,
            "target": {"type": "token", "value": token},
            "type": "chat"
        },
        token=source,
    )
    messaging.send(msg)

def send_message_room(room_id, message, source=None):
    """
        Send a chat message to the given target

        :param room: room target of the message
        :type room: smserver.models.room.Room
        :param str message: Message to send
        :param str source: token which have send the event
    """

    msg = event.Event(
        kind=event.EventKind.chat_message,
        data={
            "source": source,
            "message": message,
            "target": {"type": "room", "value": room_id},
            "type": "chat"
        },
        room_id=room_id,
        token=source,
    )
    messaging.send(msg)
