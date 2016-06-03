#!/usr/bin/env python3
# -*- coding: utf8 -*-

import logging
import logging.handlers
import sys

class Logger(object):
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

        self._logger = logging.getLogger('stepmania')
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
        return self._logger

    def _get_stderr_handler(self, **kwargs):
        return logging.StreamHandler(sys.stderr)

    def _get_file_handler(self, **kwargs):
        return logging.handlers.TimedRotatingFileHandler(
            kwargs.get("file", "log/stepmania.log"),
            when="midnight",
            backupCount=3
        )


