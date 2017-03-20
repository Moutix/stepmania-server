""" Test for chat command /free """

from smserver.chat_commands import room_update

from test.test_chat_commands import base
from test.factories.room_factory import RoomFactory
from test.factories.user_factory import user_with_room_privilege

class ChatFreeTest(base.ChatCommandTest):
    """ Chat free test """

    @property
    def chat_command(self):
        return room_update.ChatRoomFree(self.server)

    def test_change_free(self):
        """ Test to change the free of a room """

        room = RoomFactory(free=False)

        self.connection.room = room
        user_with_room_privilege(
            level=5,
            connection=self.connection,
            online=True,
            room=room,
        )

        ret = self.chat_command(self.resource, None)
        self.assertIsNone(ret)
        self.assertEqual(room.free, True)

        ret = self.chat_command(self.resource, None)
        self.assertIsNone(ret)
        self.assertEqual(room.free, False)
