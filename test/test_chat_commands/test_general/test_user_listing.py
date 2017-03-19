""" Test for chat command /help """

from smserver.chat_commands import general

from test.test_chat_commands import base
from test.factories.user_factory import UserFactory
from test.factories.room_factory import RoomFactory

class ChatUserListingTest(base.ChatCommandTest):
    """ Chat unban test """

    @property
    def chat_command(self):
        return general.ChatUserListing(self.server)

    def test_list_user_without_room(self):
        """ Test displaying the list of users """

        user1 = UserFactory(online=True)
        UserFactory(online=False)
        user3 = UserFactory(online=True)

        res = self.chat_command(self.resource, "bla")
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0], "2/-1 players online")
        self.assertRegex(res[1], user1.name)
        self.assertRegex(res[2], user3.name)

        res = self.chat_command(self.resource, "bla", limit=1)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0], "2/-1 players online")
        self.assertRegex(res[1], user1.name)


    def test_list_user_with_room(self):
        """ Test displaying the list of users """

        room = RoomFactory(max_users=42)
        self.connection.room = room

        user1 = UserFactory(online=True, room=room)
        UserFactory(online=False)
        UserFactory(online=True)
        user4 = UserFactory(online=True, room=room)

        res = self.chat_command(self.resource, "bla")
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0], "2/42 players online")
        self.assertRegex(res[1], user1.name)
        self.assertRegex(res[2], user4.name)

        res = self.chat_command(self.resource, "bla", limit=1)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0], "2/42 players online")
        self.assertRegex(res[1], user1.name)
