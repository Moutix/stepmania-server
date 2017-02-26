""" Chat event worker module """


from smserver.listener.workers import base

class ChatWorker(base.BaseWorker):
    """ Chat worker """

    need_session = True

    def handle(self, data, token=None, *, session=None):
        """ Handle a new incomming chat message """
