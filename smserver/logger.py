""" Logger module.

Use `get_logger` to get the current stepmania logger
"""

import logging
import logging.handlers
import sys

class Logger(object):
    """ Logger object use to configure the loggin handler """
    NAME = "stepmania"

    _LEVEL = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    def __init__(self, options=None):
        if not options:
            options = {"stderr": {}}

        self._logger = logging.getLogger(self.NAME)
        self._logger.setLevel(logging.DEBUG)

        for type_handler, log_options in options.items():

            handler = {
                "file": self._get_file_handler,
                "stderr": self._get_stderr_handler
            }[type_handler](**log_options)

            handler.setLevel(self._LEVEL.get(log_options.get("level"), logging.INFO))
            handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))

            self._logger.addHandler(handler)

    @property
    def logger(self):
        """ Return the logger associated with this object """

        return self._logger

    @staticmethod
    def _get_stderr_handler(**_kwargs):
        return logging.StreamHandler(sys.stderr)

    @staticmethod
    def _get_file_handler(**kwargs):
        return logging.handlers.TimedRotatingFileHandler(
            kwargs.get("file", "log/stepmania.log"),
            when="midnight",
            backupCount=3
        )

def get_logger():
    """ Get the stepmania logger """

    return logging.getLogger('stepmania')

def set_logger_options(options):
    """ Set the logger options """

    return Logger(options).logger
