""" Event module """

import json
import enum
import uuid

class EventKind(enum.Enum):
    """ Type of message that can be send """

    chat_message = 1


class Event(object):
    """ Event object, use this to send events """

    def __init__(self, kind, data=None, token=None, room_id=None, *, uuid_=None):
        if not data:
            data = {}

        self.kind = kind
        self.data = data
        self.token = token
        self.room_id = room_id
        if uuid_:
            self.uuid = uuid_
        else:
            self.uuid = uuid.uuid4().hex

    def __repr__(self):
        """ Event representation

            >>> print(Event(EventKind.chat_message, uuid_="45"))
            <Event #45 (EventKind.chat_message)>
        """

        return "<Event #{uuid} ({kind})>".format(
            uuid=self.uuid,
            kind=self.kind
        )

    def __eq__(self, other):
        return self.uuid == other.uuid

    def encode(self):
        """ Encode a message """

        return json.dumps({
            "kind": self.kind.value,
            "data": self.data,
            "token": self.token,
            "room_id": self.room_id,
            "uuid": self.uuid
        })

    @classmethod
    def decode(cls, data):
        """ Decode a message """

        event = json.loads(data)
        kind = EventKind(event.get("kind"))

        return cls(
            kind=kind,
            data=event.get("data", {}),
            token=event.get("token"),
            room_id=event.get("room_id"),
            uuid_=event.get("uuid")
        )
