""" Test for chat command /hide """

from smserver.chat_commands import room_update

from test.test_chat_commands import base
from test.factories.room_factory import RoomFactory
from test.factories.user_factory import user_with_room_privilege

class ChatRoomHiddenTest(base.ChatCommandTest):
    """ Chat room hidden test """

    @property
    def chat_command(self):
        return room_update.ChatRoomHidden(self.server)

    def test_change_hide(self):
        """ Test to change the display of a room """

        room = RoomFactory(hidden=False)

        self.connection.room = room
        user_with_room_privilege(
            level=5,
            connection=self.connection,
            online=True,
            room=room,
        )

        ret = self.chat_command(self.resource, None)
        self.assertIsNone(ret)
        self.assertEqual(room.hidden, True)

        ret = self.chat_command(self.resource, None)
        self.assertIsNone(ret)
        self.assertEqual(room.hidden, False)
