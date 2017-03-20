""" Test for chat command /delete """

from smserver.chat_commands import room_update
from smserver import models

from test.test_chat_commands import base
from test.factories.room_factory import RoomFactory
from test.factories.user_factory import user_with_room_privilege

class ChatDeleteTest(base.ChatCommandTest):
    """ Chat delete test """

    @property
    def chat_command(self):
        return room_update.ChatDeleteRoom(self.server)

    def test_delete(self):
        """ Test to delete of a room """

        room = RoomFactory()
        self.connection.room = room

        user_with_room_privilege(
            level=10,
            connection=self.connection,
            online=True,
            room=room,
        )

        ret = self.chat_command(self.resource, None)
        self.assertIsNone(ret)
        self.assertEqual(self.connection.room, None)
        self.assertIsNone(self.session.query(models.Room).get(room.id))
