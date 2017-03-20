""" Test for chat command /description """

from smserver.chat_commands import room_update

from test.test_chat_commands import base
from test.factories.room_factory import RoomFactory
from test.factories.user_factory import user_with_room_privilege

class ChatDescriptionTest(base.ChatCommandTest):
    """ Chat description test """

    @property
    def chat_command(self):
        return room_update.ChatDescription(self.server)

    def test_change_description(self):
        """ Test to change the description in a room """

        room = RoomFactory()

        self.connection.room = room
        user_with_room_privilege(
            level=5,
            connection=self.connection,
            online=True,
            room=room
        )

        ret = self.chat_command(self.resource, "New description")
        self.assertIsNone(ret)
        self.assertEqual(room.description, "New description")
