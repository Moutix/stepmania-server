""" Utils module for test """

import unittest
import testfixtures

from test import common

class SMServerTest(unittest.TestCase):
    """ Base for all the test """

    def setUp(self):
        self._log_capture = testfixtures.LogCapture()

    def assertLog(self, level, message=None): #pylint: disable=invalid-name
        """ Assert a message has been logged """

        if message:
            return self._log_capture.check(('stepmania', level, message))


        for record in self._log_capture.records:
            if record.levelname == level:
                return

        raise AssertionError("No log % as been captured" % level)

    def get_logs(self, level):
        """ Get a log that match the given level """

        logs = []
        for record in self._log_capture.records:
            if record.levelname == level:
                logs.append(record)

        return logs

    def assertNotLog(self, level, message=None): #pylint: disable=invalid-name
        """ Assert no message of this type has been record """
        with self.assertRaises(AssertionError, msg="Log %s found" % level):
            self.assertLog(level, message)

    def reset_log(self):
        """ Reset the log capture """
        self._log_capture.uninstall_all()
        self._log_capture = testfixtures.LogCapture()

    def tearDown(self):
        self._log_capture.uninstall_all()

class DBTest(SMServerTest):
    """ Base class for DBTest"""

    def setUp(self):
        # Prepare a new, clean session
        super().setUp()
        self.session = common.db.session()

    def tearDown(self):
        super().tearDown()
        common.db.session.rollback()
        # Remove it, so that the next test gets a new Session()
        common.db.session.remove()
        # Rollback the session => no changes to the database
        common.db.recreate_tables()
