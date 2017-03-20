""" Test listener module """

import mock

from smserver import event
from smserver import server
from smserver.listener import app
from smserver.smutils import smconn

from test import utils


class ListenerTest(utils.DBTest):
    """ Test listener module """

    def setUp(self):
        super().setUp()

        self.server = server.StepmaniaServer()
        self.conn = smconn.StepmaniaConn(self.server, "8.8.8.8", 42)
        self.listener = app.Listener(self.server)

    @mock.patch("smserver.messaging.Messaging.listen")
    def test_run_exceptions(self, msg_listen):
        """ Test running the listener with unexpected error"""

        self.listener.dispatch = {}

        msg1 = event.Event(event.EventKind.chat_message, data="bla")
        msg_listen.return_value = [msg1]

        self.listener.run()
        logs = self.get_logs("ERROR")
        self.assertEqual(len(logs), 1)
        self.assertEqual(
            logs[0].message,
            "Unknown event kind %s" % event.EventKind.chat_message
        )
        self.reset_log()

        worker = mock.MagicMock()
        worker.handle = mock.Mock(side_effect=Exception())

        self.listener.dispatch = {event.EventKind.chat_message: worker}

        self.listener.run()
        self.assertEqual(worker.handle.call_args[0][0], "bla")
        self.assertIn("session", worker.handle.call_args[1])
        self.assertLog("ERROR")

        self.reset_log()

        worker.need_session = False
        self.listener.run()
        self.assertEqual(worker.handle.call_args[0][0], "bla")
        self.assertNotIn("session", worker.handle.call_args[1])
        self.assertLog("ERROR")

    @mock.patch("smserver.smutils.smthread.StepmaniaServer.has_room")
    @mock.patch("smserver.messaging.Messaging.listen")
    def test_run_without_room(self, msg_listen, has_room):
        """ Test running the listener without room """

        msg1 = event.Event(event.EventKind.chat_message, data="bla", room_id=3)
        msg_listen.return_value = [msg1]

        worker = mock.MagicMock()
        self.listener.dispatch = {event.EventKind.chat_message: worker}

        has_room.return_value = False

        self.listener.run()
        self.assertNotLog("ERROR")
        msg_listen.assert_called_once()
        worker.handle.assert_not_called()

    @mock.patch("smserver.smutils.smthread.StepmaniaServer.has_room")
    @mock.patch("smserver.messaging.Messaging.listen")
    def test_run(self, msg_listen, has_room):
        """ Test running the listener """

        msg1 = event.Event(event.EventKind.chat_message, data="bla", room_id=3)
        msg2 = event.Event(event.EventKind.chat_message, data="blabla", token="aa")
        msg_listen.return_value = [msg1, msg2]

        worker = mock.MagicMock()
        self.listener.dispatch = {event.EventKind.chat_message: worker}

        has_room.return_value = True
        worker.need_session = True

        self.listener.run()
        self.assertNotLog("ERROR")
        msg_listen.assert_called_once()
        self.assertEqual(worker.handle.call_count, 2)

        args, kwargs = worker.handle.call_args_list[0]
        self.assertEqual(args[0], msg1.data)
        self.assertEqual(kwargs["token"], msg1.token)
        self.assertIn("session", kwargs)

        args, kwargs = worker.handle.call_args_list[1]
        self.assertEqual(args[0], msg2.data)
        self.assertEqual(kwargs["token"], msg2.token)
        self.assertIn("session", kwargs)

    @mock.patch("smserver.messaging.Messaging.stop")
    def test_stop(self, messaging_stop):
        """ Test stopping the listenner thread """

        messaging_stop.assert_not_called()
        self.listener.stop()
        messaging_stop.assert_called_with()
