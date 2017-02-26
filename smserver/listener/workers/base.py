""" Base worker module """

import abc

class BaseWorker(metaclass=abc.ABCMeta):
    """ Base worker

        Inherit from this class to add a worker
    """

    need_session = False

    @abc.abstractmethod
    def handle(self, data, token=None, *, session=None):
        """ Handle an event

            :param dict data: data in the event
            :param str token: token which send the data
        """
