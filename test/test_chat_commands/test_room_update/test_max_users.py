""" Test for chat command /max_users """

from smserver.chat_commands import room_update

from test.test_chat_commands import base
from test.factories.room_factory import RoomFactory
from test.factories.user_factory import user_with_room_privilege

class ChatMaxUsersTest(base.ChatCommandTest):
    """ Chat max_users test """

    @property
    def chat_command(self):
        return room_update.ChatMaxUsers(self.server)

    def test_change_max_users(self):
        """ Test to change the nb max of users in a room """

        room = RoomFactory()

        self.connection.room = room
        user_with_room_privilege(
            level=5,
            connection=self.connection,
            online=True,
            room=room
        )

        ret = self.chat_command(self.resource, "invalid_number")
        self.assertEqual(len(ret), 1)
        self.assertRegex(ret[0], "Invalid number")

        ret = self.chat_command(self.resource, "54")
        self.assertIsNone(ret)
        self.assertEqual(room.max_users, 54)
