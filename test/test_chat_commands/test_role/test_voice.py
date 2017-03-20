""" Test for chat command /voice """

from smserver.chat_commands import role

from test.test_chat_commands import base
from test.factories.room_factory import RoomFactory
from test.factories.user_factory import user_with_room_privilege

class ChatVoiceTest(base.ChatCommandTest):
    """ Chat voice test """

    @property
    def chat_command(self):
        return role.ChatVoice(self.server)

    def test_set_op(self):
        """ Test to voice a user in a room """

        room = RoomFactory()

        self.connection.room = room
        user_with_room_privilege(
            level=6,
            connection=self.connection,
            online=True,
            room=room
        )

        target_user_admin = user_with_room_privilege(
            level=10,
            online=True,
            room=room
        )
        target_user = user_with_room_privilege(
            level=4,
            online=True,
            room=room
        )

        ret = self.chat_command(self.resource, "invalid_user")
        self.assertEqual(len(ret), 1)
        self.assertRegex(ret[0], "Unknown user")

        ret = self.chat_command(self.resource, target_user_admin.name)
        self.assertEqual(len(ret), 1)
        self.assertRegex(ret[0], "Not authorize")
        self.assertEqual(target_user_admin.level(room.id), 10)

        ret = self.chat_command(self.resource, target_user.name)
        self.assertIsNone(ret)
        self.assertEqual(target_user.level(room.id), 1)
