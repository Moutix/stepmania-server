""" Test for chat command /leave """

from smserver.chat_commands import room_update

from test.test_chat_commands import base
from test.factories.room_factory import RoomFactory
from test.factories.user_factory import user_with_room_privilege

class ChatLeaveTest(base.ChatCommandTest):
    """ Chat leave test """

    @property
    def chat_command(self):
        return room_update.ChatLeaveRoom(self.server)

    def test_leave(self):
        """ Test to leave a room """

        room = RoomFactory()
        self.connection.room = room

        user_with_room_privilege(
            level=1,
            connection=self.connection,
            online=True,
            room=room,
        )

        ret = self.chat_command(self.resource, None)
        self.assertIsNone(ret)
        self.assertEqual(self.connection.room, None)
