""" Test for chat command unban """

from smserver.chat_commands import ban
from smserver import models

from test.test_chat_commands import base
from test.factories.user_factory import UserFactory
from test.factories.room_factory import RoomFactory


class ChatUnBanTest(base.ChatCommandTest):
    """ Chat unban test """

    @property
    def chat_command(self):
        return ban.ChatUnBan(self.server)

    def test_unban_without_room(self):
        """ Test banning a user without room """

        res = self.chat_command(self.resource, "User")
        self.assertEqual(len(res), 1)
        self.assertRegex(res[0], "Unknown user")

        UserFactory(online=True, connection=self.connection)

        target_user = UserFactory(online=True)

        models.Ban.ban(self.session, user_id=target_user.id)
        self.assertTrue(models.Ban.is_ban(self.session, user_id=target_user.id))

        res = self.chat_command(self.resource, target_user.name)

        self.assertFalse(models.Ban.is_ban(self.session, user_id=target_user.id))
        self.assertIsNone(res)

    def test_unban_with_room(self):
        """ Test banning a user from a room """

        room = RoomFactory()
        self.connection.room = room

        UserFactory(online=True, connection=self.connection, room=room)

        target_user = UserFactory(online=True)

        models.Ban.ban(self.session, user_id=target_user.id, room_id=room.id)
        self.assertTrue(models.Ban.is_ban(self.session, user_id=target_user.id, room_id=room.id))

        res = self.chat_command(self.resource, target_user.name)
        self.assertFalse(models.Ban.is_ban(self.session, user_id=target_user.id, room_id=room.id))
        self.assertIsNone(res)
