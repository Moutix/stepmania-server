""" Base test for chat commands """

from smserver import server
from smserver.resources.chat_resource import ChatResource


from test import utils
from test.factories.connection_factory import ConnectionFactory
from test.factories.user_factory import user_with_room_privilege
from test.factories.user_factory import UserFactory


class ChatCommandTest(utils.DBTest):
    """ Base class for resource testing """

    def setUp(self):
        super().setUp()

        self.server = server.StepmaniaServer()

        self.connection = ConnectionFactory()
        self.token = self.connection.token

        self.resource = ChatResource(self.server, self.token, self.session)

    @property
    def chat_command(self):
        """ Chat Command to use """
        raise NotImplementedError("Chat command is reuired")

    def test_can_without_room(self):
        """ Test can function without room """

        if not self.chat_command.permission:
            self.assertEqual(self.chat_command.can(self.connection), not self.chat_command.room)
            return

        self.assertFalse(self.chat_command.can(self.connection))

        user = UserFactory(connection=self.connection, online=True)
        self.assertFalse(self.chat_command.can(self.connection))

        user.rank = self.chat_command.permission.value
        if self.chat_command.room:
            self.assertFalse(self.chat_command.can(self.connection))
        else:
            self.assertTrue(self.chat_command.can(self.connection))

    def test_can_with_room(self):
        """ Test can function with room """

        if not self.chat_command.permission:
            self.assertTrue(self.chat_command.can(self.connection))
            return

        self.assertFalse(self.chat_command.can(self.connection))

        user = user_with_room_privilege(
            level=self.chat_command.permission.value,
            online=True,
            connection=self.connection,
        )
        self.connection.room = user.room
        self.session.commit()
        self.assertTrue(self.chat_command.can(self.connection))
