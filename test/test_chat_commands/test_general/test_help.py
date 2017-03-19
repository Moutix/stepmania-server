""" Test for chat command /help """

import mock

from smserver.chat_commands import general

from test.test_chat_commands import base


class ChatHelpTest(base.ChatCommandTest):
    """ Chat unban test """

    @property
    def chat_command(self):
        return general.ChatHelp(self.server)

    def test_help(self):
        """ Test displaying the help """

        mock1 = mock.MagicMock()
        mock1.can.return_value = False
        mock1.helper = "helper 1"

        mock2 = mock.MagicMock()
        mock2.can.return_value = True
        mock2.helper = "helper 2"

        mock3 = mock.MagicMock()
        mock3.can.return_value = True
        mock3.helper = "helper 3"

        self.server.chat_commands = {
            "mock1": mock1,
            "mock2": mock2,
            "mock3": mock3,
        }

        # Invalid command
        res = self.chat_command(self.resource, "invalid command")
        self.assertEqual(len(res), 1)
        self.assertRegex(res[0], "Unknown command")

        # Unauthorized command
        res = self.chat_command(self.resource, "mock1")
        self.assertEqual(len(res), 1)
        self.assertRegex(res[0], "Unknown command")

        # Authorized command
        res = self.chat_command(self.resource, "mock2")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], "/mock2: helper 2")

        # List commands
        res = self.chat_command(self.resource, None)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0], "/mock2: helper 2")
        self.assertEqual(res[1], "/mock3: helper 3")
