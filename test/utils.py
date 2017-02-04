""" Utils module for test """

import unittest

from test import common

class DBTest(unittest.TestCase):
    """ Base class for DBTest"""

    def setUp(self):
        # Prepare a new, clean session
        self.session = common.Session()

    def tearDown(self):
        # Rollback the session => no changes to the database
        self.session.rollback()
        # Remove it, so that the next test gets a new Session()
        common.Session.remove()
