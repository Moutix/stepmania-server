""" Test for chat command ban """

import mock

from smserver.chat_commands import ban
from smserver import models

from test.test_chat_commands import base
from test.factories.connection_factory import ConnectionFactory
from test.factories.user_factory import user_with_room_privilege
from test.factories.user_factory import UserFactory
from test.factories.room_factory import RoomFactory


class ChatBanTest(base.ChatCommandTest):
    """ Chat ban test """

    @property
    def chat_command(self):
        return ban.ChatBan(self.server)

    @mock.patch("smserver.server.StepmaniaServer.disconnect_user")
    def test_ban_without_room(self, disconnect_user):
        """ Test banning a user without room """

        res = self.chat_command(self.resource, "User")
        self.assertEqual(len(res), 1)
        self.assertRegex(res[0], "Unknown user")

        disconnect_user.assert_not_called()

        user = UserFactory(online=True, connection=self.connection)

        target_user = UserFactory(online=True)

        res = self.chat_command(self.resource, target_user.name)
        self.assertEqual(len(res), 1)
        self.assertRegex(res[0], "Not authorize")
        disconnect_user.assert_not_called()

        user.rank = self.chat_command.permission.value
        res = self.chat_command(self.resource, target_user.name)

        self.assertTrue(models.Ban.is_ban(self.session, user_id=target_user.id))
        disconnect_user.assert_called_with(target_user.id)

        self.assertIsNone(res)

    @mock.patch("smserver.server.StepmaniaServer.disconnect_user")
    def test_ban_with_room(self, disconnect_user):
        """ Test banning a user from a room """

        room = RoomFactory()
        self.connection.room = room

        user_with_room_privilege(
            connection=self.connection,
            online=True,
            room=room,
            level=self.chat_command.permission.value,
        )
        target_connection = ConnectionFactory(room=room)
        target_user = user_with_room_privilege(
            room=room,
            online=True,
            connection=target_connection,
        )

        self.chat_command(self.resource, target_user.name)
        self.assertFalse(models.Ban.is_ban(self.session, user_id=target_user.id))
        self.assertTrue(models.Ban.is_ban(self.session, user_id=target_user.id, room_id=room.id))

        self.assertIsNone(target_user.room)
        self.assertIsNone(target_connection.room)

        disconnect_user.assert_not_called()
