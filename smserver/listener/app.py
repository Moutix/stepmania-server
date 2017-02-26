""" Listener module.

This module is responsible of listening for incomming event
"""

from threading import Thread

from smserver import event
from smserver import messaging
from smserver.listener.workers import chat


class Listener(Thread):
    """ Secondary thread, hold by the main server. """

    def __init__(self, server):
        Thread.__init__(self)

        self.server = server

        self.dispatch = {
            event.EventKind.chat_message: chat.ChatWorker(),
        }

    def run(self):
        """ Start to listen for incomming event """

        self.server.log.debug("Start listener")

        for evt in messaging.listen():
            if evt.room_id and not self.server.has_room(evt.room_id):
                self.server.log.debug(
                    "Ignore event %s: no connection on the room %s",
                    evt,
                    evt.room_id
                )
                continue

            if evt.kind not in self.dispatch:
                self.server.log.error("Unknown event kind %s", evt.kind)
                continue

            worker = self.dispatch[evt.kind]

            try:
                if worker.need_session:
                    with self.server.db.session_scope() as session:
                        worker.handle(evt.data, token=evt.token, session=session)
                else:
                    worker.handle(evt.data, token=evt.token)
            except Exception: #pylint: disable=broad-except
                self.server.log.exception('Error while handling %s', evt)

    def stop(self):
        """ Stop the thread """

        self.server.log.debug("Closing thread: %s", self)
        messaging.stop()
